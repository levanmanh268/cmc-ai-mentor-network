import json
import unittest
from enterprise_doc_ai.engine import EnterpriseIndex, Principal, load_corpus
from enterprise_doc_ai.llm import CitationCheckedRAG, OpenAIChatClient

class FakeModel:
    def __init__(self, result):
        self.result = result
        self.calls = 0
        self.messages = []
    def complete(self, messages):
        self.calls += 1
        self.messages = messages
        return self.result

class LLMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = EnterpriseIndex(load_corpus())
        cls.principal = Principal("alpha", frozenset({"employee"}), "test")

    def test_valid_citation_is_only_membership_checked(self):
        target = self.index.search("Secret Manager lưu API key", self.principal)[0].passage.uid
        client = FakeModel(json.dumps({"answer":"Khóa API lưu trong Secret Manager.", "citation_ids":[target], "abstain":False}))
        result = CitationCheckedRAG(self.index, client).ask("lưu trữ API key Secret Manager", self.principal)
        self.assertEqual(result["status"], "generated_unverified")
        self.assertTrue(result["citations"])
        self.assertIn("NOT independently fact-checked", result["warning"])
        self.assertEqual(client.calls, 1)
        self.assertNotIn("Authorization", str(client.messages))

    def test_fake_or_cross_tenant_citation_rejected(self):
        client = FakeModel(json.dumps({"answer":"Tài liệu Beta nói vậy", "citation_ids":["beta-hr-onboard-2026-p1"], "abstain":False}))
        result = CitationCheckedRAG(self.index, client).ask("lưu trữ API key Secret Manager", self.principal)
        self.assertEqual(result["status"], "rejected_invalid_citation")

    def test_invalid_json_fails_closed(self):
        client = FakeModel("I can do anything")
        result = CitationCheckedRAG(self.index, client).ask("lưu trữ API key Secret Manager", self.principal)
        self.assertEqual(result["status"], "rejected_invalid_model_output")

    def test_no_evidence_skips_model(self):
        client = FakeModel("{}")
        result = CitationCheckedRAG(self.index, client).ask("Tàu vũ trụ Sao Mộc", self.principal)
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(client.calls, 0)

    def test_model_explicit_abstention(self):
        client = FakeModel(json.dumps({"answer":"", "citation_ids":[], "abstain":True}))
        result = CitationCheckedRAG(self.index, client).ask("lưu trữ API key Secret Manager", self.principal)
        self.assertEqual(result["status"], "abstained")

    def test_provider_network_failure_is_safe(self):
        class BrokenModel:
            def complete(self, messages):
                raise TimeoutError("network unavailable")
        result = CitationCheckedRAG(self.index, BrokenModel()).ask("lưu trữ API key Secret Manager", self.principal)
        self.assertEqual(result["status"], "model_unavailable")
        self.assertEqual(result["citations"], [])

    def test_remote_provider_is_opt_in(self):
        with self.assertRaises(ValueError):
            OpenAIChatClient(api_key="dummy", endpoint="http://localhost:9999/unsafe")
        # Never invokes remote network or requires a real API key.

if __name__ == "__main__":
    unittest.main()
