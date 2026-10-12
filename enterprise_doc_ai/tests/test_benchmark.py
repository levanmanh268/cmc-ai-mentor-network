import unittest
from enterprise_doc_ai.engine import EnterpriseIndex, load_corpus
from enterprise_doc_ai.benchmark import evaluate, load_cases

class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.idx = EnterpriseIndex(load_corpus())
        cls.cases = load_cases()

    def test_dataset_size(self):
        self.assertEqual(len(self.cases), 80)
        self.assertEqual(sum(bool(c["gold_families"]) for c in self.cases), 64)
        self.assertEqual(sum(not c["gold_families"] for c in self.cases), 16)

    def test_metrics_privacy(self):
        heldout = [c for c in self.cases if c["split"] == "test"]
        for method in ("bm25", "char", "hybrid"):
            r = evaluate(self.idx, heldout, method, k=3)
            self.assertEqual(r["access_leakage_count"], 0)
            self.assertEqual(r["future_document_exposure_count"], 0)
            for key in ("hit_at_k", "mrr_at_k", "recall_at_k", "ndcg_at_k", "negative_abstention_rate"):
                self.assertIsNotNone(r[key])
                self.assertTrue(0 <= r[key] <= 1, key)

    def test_one_answerable_and_negative(self):
        report = evaluate(self.idx, [self.cases[0], self.cases[-1]])
        self.assertEqual(report["answerable_cases"], 1)
        self.assertEqual(report["negative_cases"], 1)

    def test_empty_eval_error(self):
        with self.assertRaises(ValueError): evaluate(self.idx, [])

if __name__ == "__main__":
    unittest.main()
