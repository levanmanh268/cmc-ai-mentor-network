"""Regression coverage for retrieval, safety, evaluation, and optional dense embeddings."""
import tempfile
import unittest
from pathlib import Path
from cagent_lab.core import BM25Index, TFIDFIndex, DenseIndex, GroundedAssistant, SafeAgent, Document, chunk_text, load_document
from cagent_lab.evaluate import evaluate, load_corpus

DOCS = [
    Document("a#chunk-1", "Onboarding information must go to the HR portal.", "a"),
    Document("b#chunk-1", "Keep access tokens secret in an approved manager.", "b"),
]

class DummyEncoder:
    def encode(self, texts):
        return [[1., 0.] if "portal" in x.lower() else [0., 1.] for x in texts]

class CoreTests(unittest.TestCase):
    def test_chunking_overlap(self):
        chunks = chunk_text("a b c d e", "doc", size=3, overlap=1)
        self.assertEqual([x.text for x in chunks], ["a b c", "c d e", "e"])
        with self.assertRaises(ValueError):
            chunk_text("anything", "doc", size=2, overlap=2)

    def test_bm25_relevance(self):
        self.assertEqual(BM25Index(DOCS).search("onboarding portal")[0].document.source, "a")

    def test_tfidf_relevance(self):
        self.assertEqual(TFIDFIndex(DOCS).search("secret token manager")[0].document.source, "b")

    def test_no_evidence(self):
        answer = GroundedAssistant(BM25Index(DOCS)).answer("quantum banana astrophysics")
        self.assertEqual(answer["status"], "abstained")
        self.assertEqual(answer["citations"], [])

    def test_evidence_has_source(self):
        answer = GroundedAssistant(BM25Index(DOCS)).answer("portal onboarding")
        self.assertEqual(answer["status"], "answered")
        self.assertEqual(answer["mode"], "extractive")
        self.assertEqual(answer["citations"][0]["source"], "a")

    def test_agent_allowlist(self):
        agent = SafeAgent(GroundedAssistant(BM25Index(DOCS)))
        self.assertEqual(agent.run("list_sources")["result"], ["a", "b"])
        self.assertEqual(agent.run("run_shell")["error"], "Tool not allowed")

    def test_dense_encoder_injection(self):
        hits = DenseIndex(DOCS, DummyEncoder()).search("portal")
        self.assertEqual(hits[0].document.source, "a")

    def test_evaluator(self):
        cases = [{"id": "1", "question": "portal", "relevant_sources": ["a"]}, {"id": "2", "question": "unseenegg", "relevant_sources": []}]
        result = evaluate(BM25Index(DOCS), cases, 2)
        self.assertEqual(result["hit_at_k"], 0.5)
        self.assertEqual(result["negative_abstention_accuracy"], 1.0)

    def test_document_loader(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "hello.md"
            path.write_text("sample hello", encoding="utf-8")
            self.assertEqual(load_document(path), "sample hello")
            with self.assertRaises(ValueError):
                load_document(path.with_suffix(".exe"))

    def test_dataset_exists(self):
        self.assertGreaterEqual(len(load_corpus(Path(__file__).parents[1] / "data" / "knowledge")), 3)

if __name__ == "__main__":
    unittest.main()
