import copy
import math
import tempfile
import unittest
from pathlib import Path
from model_pretraining_lab.core import BigramLM, Tokenizer, train
from model_posttraining_lab.core import (
    average_response_nll, dpo_loss_and_gradient, fit, load_pairs,
    packed_response, preference_margin, response_logprob,
)

class PosttrainingTests(unittest.TestCase):
    def setUp(self):
        self.rows=load_pairs()
        self.tok=Tokenizer(sorted(set("Q:abc\nA:yesto ")))
        self.model=BigramLM(self.tok.size,seed=101)

    def test_splits_and_no_shared_prompts(self):
        self.assertEqual(len(self.rows),12)
        self.assertEqual(sum(x["split"]=="train" for x in self.rows),8)
        self.assertEqual(sum(x["split"]=="val" for x in self.rows),2)
        self.assertEqual(sum(x["split"]=="test" for x in self.rows),2)
        self.assertEqual(len({x["prompt"].casefold() for x in self.rows}),12)

    def test_sft_response_only_masking(self):
        seq,start=packed_response(self.tok,"abc","yes")
        self.assertGreater(start,1)
        full=self.model.gradient(seq,start=1)
        masked=self.model.gradient(seq,start=start)
        self.assertNotEqual(full,masked)
        self.assertGreater(len(seq)-start,0)

    def test_sft_update_improves_single_response_nll(self):
        example={"prompt":"abc","chosen":"yes"}
        prior=-response_logprob(self.model,self.tok,example["prompt"],example["chosen"])
        seq,start=packed_response(self.tok,example["prompt"],example["chosen"])
        self.model.step(self.model.gradient(seq,start),0.04)
        after=-response_logprob(self.model,self.tok,example["prompt"],example["chosen"])
        self.assertLess(after,prior)

    def test_dpo_gradient_matches_finite_difference(self):
        example={"prompt":"abc","chosen":"yes","rejected":"no"}
        reference=BigramLM(self.tok.size,weights=copy.deepcopy(self.model.weights))
        self.model.weights[3][4]+=0.13
        loss,grad=dpo_loss_and_gradient(self.model,reference,self.tok,example,beta=0.2)
        self.assertTrue(math.isfinite(loss))
        entry=(3,4); eps=1e-5; original=self.model.weights[entry[0]][entry[1]]
        self.model.weights[entry[0]][entry[1]]=original+eps
        plus,_=dpo_loss_and_gradient(self.model,reference,self.tok,example,beta=0.2)
        self.model.weights[entry[0]][entry[1]]=original-eps
        minus,_=dpo_loss_and_gradient(self.model,reference,self.tok,example,beta=0.2)
        self.model.weights[entry[0]][entry[1]]=original
        self.assertAlmostEqual(grad[entry[0]][entry[1]],(plus-minus)/(2*eps),places=5)

    def test_initial_dpo_loss_is_log_two(self):
        ex={"prompt":"abc","chosen":"yes","rejected":"no"}
        reference=BigramLM(self.tok.size,weights=copy.deepcopy(self.model.weights))
        loss,_=dpo_loss_and_gradient(self.model,reference,self.tok,ex)
        self.assertAlmostEqual(loss,math.log(2.0),places=9)

    def test_end_to_end_pretrain_sft_dpo(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)/"pre"
            train(base,epochs=2)
            report=fit(base/"tiny_pretrained.json",Path(folder)/"post",sft_epochs=2,dpo_epochs=2)
            self.assertEqual(report["train_examples"],8)
            self.assertEqual(report["val_examples"],2)
            self.assertEqual(report["test_examples"],2)
            self.assertEqual(report["stages"],["supervised_fine_tuning","direct_preference_optimization"])
            self.assertTrue(math.isfinite(report["validation_preference_margin_after_dpo"]))
            self.assertTrue((Path(folder)/"post"/"toy_posttrained.json").exists())
            self.assertLess(report["sft_train_nll_final"], report["sft_train_nll_initial"])

    def test_duplicate_preference_ids_and_normalized_prompts(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/"pairs.jsonl"
            cases=[dict(sample) for sample in self.rows]
            cases[1]["id"]=cases[0]["id"]
            file.write_text("\n".join(json.dumps(x) for x in cases)+"\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_pairs(file)
            cases[1]["id"]="unique-replacement"
            cases[1]["prompt"]="  "+" ".join(cases[0]["prompt"].upper().split())+"  "
            file.write_text("\n".join(json.dumps(x) for x in cases)+"\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_pairs(file)
            cases=[dict(sample) for sample in self.rows]
            cases[0]["rejected"]=cases[0]["chosen"].upper()+"  "
            file.write_text("\n".join(json.dumps(x) for x in cases)+"\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_pairs(file)

    def test_invalid_prompts_and_numerical_parameters(self):
        with self.assertRaises(ValueError):
            packed_response(self.tok, " ", "yes")
        with self.assertRaises(ValueError):
            packed_response(self.tok, "abc", "x"*501)
        for beta in (float("nan"), float("inf"), -1):
            with self.subTest(beta=beta), self.assertRaises(ValueError):
                dpo_loss_and_gradient(self.model,self.model,self.tok,self.rows[0],beta=beta)
        with self.assertRaises(ValueError):
            fit("unused-checkpoint",lr=float("nan"))
        with self.assertRaises(ValueError):
            fit("unused-checkpoint",sft_epochs=True)

    def test_invalid_data_and_hyperparameters(self):
        with self.assertRaises(ValueError):
            packed_response(self.tok,"abc","")
        with self.assertRaises(ValueError):
            dpo_loss_and_gradient(self.model,self.model,self.tok,self.rows[0],beta=0)
        with self.assertRaises(ValueError):
            fit("does-not-exist.json",sft_epochs=0)

if __name__=="__main__":
    unittest.main()
