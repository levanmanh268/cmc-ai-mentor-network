import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from model_pretraining_lab.core import (
    BigramLM, Tokenizer, cross_entropy, load_checkpoint,
    read_corpus, softmax, train, transitions,
)

class PretrainingTests(unittest.TestCase):
    def test_splits_and_vocab_train_only(self):
        docs = read_corpus()
        self.assertEqual({x["split"] for x in docs}, {"train","val","test"})
        tok = Tokenizer.fit(docs)
        self.assertTrue(all(c in tok.vocab for d in docs if d["split"]=="train" for c in d["text"]))
        self.assertEqual(len(tok.encode("abc")), 5)
        self.assertEqual(tok.encode("☃", wrap=False), [2])

    def test_no_cross_document_transitions(self):
        tok = Tokenizer.fit(read_corpus())
        docs = read_corpus()
        all_pairs = transitions(docs,tok,"train")
        expected = sum(len(tok.encode(d["text"]))-1 for d in docs if d["split"]=="train")
        self.assertEqual(len(all_pairs), expected)

    def test_learning_reduces_training_nll_and_saves_checkpoint(self):
        with tempfile.TemporaryDirectory() as folder:
            result = train(folder, epochs=4)
            self.assertLess(result["train_nll_final"],result["train_nll_initial"])
            self.assertTrue(math.isfinite(result["val_perplexity"]))
            model, tok, payload = load_checkpoint(Path(folder)/"tiny_pretrained.json")
            self.assertEqual(model.size,tok.size)
            self.assertEqual(payload["architecture"],"bigram_causal_lm")
            self.assertEqual(result["test_docs"],2)
            self.assertTrue((Path(folder)/"metrics.json").is_file())

    def test_nll_gradient_finite_differences(self):
        model = BigramLM(5, seed=7)
        seq=[0,3,4,1]
        grads=model.gradient(seq)
        i,j=3,4
        eps=1e-5
        original=model.weights[i][j]
        model.weights[i][j]=original+eps
        plus=-model.sequence_logprob(seq)
        model.weights[i][j]=original-eps
        minus=-model.sequence_logprob(seq)
        model.weights[i][j]=original
        self.assertAlmostEqual(grads[i][j],(plus-minus)/(2*eps),places=5)

    def test_causal_bigram_does_not_see_future(self):
        model=BigramLM(5,seed=123)
        self.assertAlmostEqual(model.logprob(3,4),model.logprob(3,4),places=12)
        tokens1=[0,3,4]
        tokens2=[0,3,2]
        self.assertAlmostEqual(model.logprob(tokens1[0],tokens1[1]),
                               model.logprob(tokens2[0],tokens2[1]),places=12)

    def test_corrupted_checkpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/"bad.json"
            file.write_text('{"architecture":"bigram_causal_lm","weights":[]}',encoding="utf-8")
            with self.assertRaises(ValueError):
                load_checkpoint(file)

    def test_schema_and_duplicate_data_rejected(self):
        import tempfile
        docs=read_corpus()
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/"repeated.jsonl"
            file.write_text(json.dumps(docs[0])+"\n"+json.dumps(docs[0])+"\n",encoding="utf-8")
            with self.assertRaises(ValueError):
                read_corpus(file)

    def test_atomic_gradient_fail_closed(self):
        model = BigramLM(5, seed=7)
        before = [row[:] for row in model.weights]
        invalid = [row[:] for row in model.gradient([0,3,4,1])]
        cases = [invalid[:-1], [[0.0] * 5 for _ in range(4)] + [[0.0] * 4],
                 [[float("nan")] + row[1:] for row in invalid]]
        for gradients in cases:
            with self.subTest(case=len(gradients)), self.assertRaises(ValueError):
                model.step(gradients, 0.1)
            self.assertEqual(model.weights, before)
        with self.assertRaises(ValueError):
            model.step(invalid, float("inf"))
        self.assertEqual(model.weights, before)
        with self.assertRaises(ValueError):
            softmax([1.0, float("nan")])
        with self.assertRaises(ValueError):
            softmax([1.0, float("inf")])

    def test_checkpoint_provenance_and_objective_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            train(folder, epochs=1)
            checkpoint = Path(folder)/"tiny_pretrained.json"
            original = json.loads(checkpoint.read_text(encoding="utf-8"))
            for field, invalid in [("objective", "other_loss"),
                                   ("train_corpus_sha256", "not-a-hash"),
                                   ("seed", True)]:
                with self.subTest(field=field):
                    changed = {**original, field: invalid}
                    checkpoint.write_text(json.dumps(changed), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_checkpoint(checkpoint)
            checkpoint.write_text(json.dumps(original), encoding="utf-8")
            model, _, _ = load_checkpoint(checkpoint)
            self.assertGreater(model.size, 4)

    def test_invalid_configuration_fails_closed(self):
        with self.assertRaises(ValueError):
            BigramLM(2)
        with self.assertRaises(ValueError):
            Tokenizer(["a","a"])
        with self.assertRaises(ValueError):
            train(epochs=0)
        with self.assertRaises(ValueError):
            softmax([])

if __name__=="__main__":
    unittest.main()
