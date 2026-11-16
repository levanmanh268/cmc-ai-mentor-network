"""Actual SFT and Direct Preference Optimization on a tiny causal bigram.

Objective math is real; capabilities are severely limited by 1-token context.
Use only synthetic preference pairs. No human ratings, RLHF service or FUNiX systems.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
from pathlib import Path
import random

from model_pretraining_lab.core import BigramLM, Tokenizer, load_checkpoint

def load_pairs(path=None):
    src = Path(path) if path else Path(__file__).parent/"data"/"preferences.jsonl"
    if not src.is_file() or src.is_symlink() or src.stat().st_size > 500000:
        raise ValueError("Invalid preference dataset")
    rows = [json.loads(row) for row in src.read_text(encoding="utf-8").splitlines() if row.strip()]
    if not 3 <= len(rows) <= 10000:
        raise ValueError("Invalid preference dataset size")
    prompts, identifiers, splits = set(), set(), set()
    for sample in rows:
        if not isinstance(sample, dict) or set(sample) != {"id","split","prompt","chosen","rejected"}:
            raise ValueError("Invalid SFT/DPO sample")
        if sample["split"] not in ("train","val","test"):
            raise ValueError("Invalid sample split")
        for field in ("id","prompt","chosen","rejected"):
            if not isinstance(sample[field], str) or not 3 <= len(sample[field]) <= 500:
                raise ValueError("Invalid sample field")
        if sample["chosen"] == sample["rejected"]:
            raise ValueError("Identical preference responses")
        key = " ".join(sample["prompt"].casefold().split())
        if (key in prompts or sample["id"] in identifiers or
            not sample["chosen"].strip() or not sample["rejected"].strip() or
            " ".join(sample["chosen"].casefold().split()) == " ".join(sample["rejected"].casefold().split())):
            raise ValueError("Duplicate ID, overlapping prompt, or indistinguishable preference")
        prompts.add(key); identifiers.add(sample["id"]); splits.add(sample["split"])
    if splits != {"train","val","test"}:
        raise ValueError("Train, validation and test required")
    return rows

def packed_response(tokenizer: Tokenizer, prompt: str, response: str):
    """Supervise assistant response tokens only, no loss on prompt tokens."""
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 500:
        raise ValueError("Empty or invalid prompt")
    if not isinstance(response, str) or not response.strip() or len(response) > 500:
        raise ValueError("Empty or invalid response")
    prefix = tokenizer.encode("Q:"+prompt+"\nA:", wrap=False)
    answer = tokenizer.encode(response, wrap=False)
    tokens = [0] + prefix + answer + [1]
    first_label = 1 + len(prefix)
    if first_label >= len(tokens):
        raise ValueError("Response empty")
    return tokens, first_label

def response_logprob(model: BigramLM, tok: Tokenizer, prompt: str, answer: str):
    sequence, start = packed_response(tok,prompt,answer)
    return model.sequence_logprob(sequence, start=start)

def average_response_nll(model, tok, pairs):
    if not pairs:
        raise ValueError("No evaluation examples")
    return -sum(response_logprob(model,tok,x["prompt"],x["chosen"]) for x in pairs) / sum(
        len(tok.encode(x["chosen"],wrap=False))+1 for x in pairs
    )

def preference_margin(model, tok, pairs):
    if not pairs:
        raise ValueError("No preference examples")
    return sum(response_logprob(model,tok,x["prompt"],x["chosen"])-
               response_logprob(model,tok,x["prompt"],x["rejected"]) for x in pairs)/len(pairs)

def dpo_loss_and_gradient(policy, reference, tok, example, beta=0.1):
    """Exact DPO scalar & analytical gradient for bigram W.

    loss = -log(sigmoid(beta*((logπ(y+)−logπ(y−))−(logπref(y+)−logπref(y−)))))
    """
    if not isinstance(beta, (int, float)) or not math.isfinite(beta) or not 0 < beta <= 5:
        raise ValueError("Invalid DPO beta")
    chosen, ci = packed_response(tok,example["prompt"],example["chosen"])
    rejected, ri = packed_response(tok,example["prompt"],example["rejected"])
    pol_margin = policy.sequence_logprob(chosen,ci) - policy.sequence_logprob(rejected,ri)
    ref_margin = reference.sequence_logprob(chosen,ci) - reference.sequence_logprob(rejected,ri)
    z = beta * (pol_margin - ref_margin)
    loss = math.log1p(math.exp(-abs(z))) + max(-z,0.0)  # stable softplus(-z)
    derivative = beta / (1.0 + math.exp(max(min(z,60),-60)))  # beta * sigmoid(-z)
    gc = policy.gradient(chosen,ci)  # d(-logp_chosen)/dW
    gr = policy.gradient(rejected,ri)
    grad = [[derivative * (gc[i][j]-gr[i][j]) for j in range(policy.size)]
            for i in range(policy.size)]
    return loss,grad

def fit(pretrained_path, output_dir="artifacts/posttraining", sft_epochs=2,
        dpo_epochs=2, lr=0.12, beta=0.1, seed=2026):
    if (type(sft_epochs) is not int or type(dpo_epochs) is not int or
        not 1 <= sft_epochs <= 25 or not 1 <= dpo_epochs <= 25 or
        not isinstance(lr, (int, float)) or not math.isfinite(lr) or not 0 < lr <= 2 or
        not isinstance(beta, (int, float)) or not math.isfinite(beta) or not 0 < beta <= 5):
        raise ValueError("Invalid training hyperparameters")
    policy, tok, checkpoint = load_checkpoint(pretrained_path)
    rows = load_pairs()
    training = [r for r in rows if r["split"]=="train"]
    valid = [r for r in rows if r["split"]=="val"]
    if not training or not valid:
        raise ValueError("Empty train/val partition")
    rng = random.Random(seed)
    before_sft = average_response_nll(policy,tok,training)
    for _ in range(sft_epochs):
        rng.shuffle(training)
        for row in training:
            packed,start=packed_response(tok,row["prompt"],row["chosen"])
            grad=policy.gradient(packed,start)
            n = len(packed)-start
            policy.step([[value/n for value in part] for part in grad],lr)
    after_sft = average_response_nll(policy,tok,training)
    reference = BigramLM(tok.size,weights=copy.deepcopy(policy.weights))
    ref_frozen = copy.deepcopy(reference.weights)
    before_dpo=preference_margin(policy,tok,valid)
    losses=[]
    for _ in range(dpo_epochs):
        rng.shuffle(training)
        for example in training:
            loss, grad = dpo_loss_and_gradient(policy,reference,tok,example,beta=beta)
            if not math.isfinite(loss):
                raise RuntimeError("Nonfinite DPO loss")
            policy.step(grad,lr)
            losses.append(loss)
    if reference.weights != ref_frozen:
        raise RuntimeError("Reference weights mutated")
    after_dpo=preference_margin(policy,tok,valid)
    result = {
        "pretrained_architecture": checkpoint["architecture"],
        "stages":["supervised_fine_tuning", "direct_preference_optimization"],
        "objective":"SFT assistant-only negative log likelihood; DPO logistic preference loss",
        "source":"synthetic_handwritten_preferences",
        "train_examples":len(training),"val_examples":len(valid),
        "test_examples":sum(row["split"]=="test" for row in rows),
        "sft_epochs":sft_epochs,"dpo_epochs":dpo_epochs,"beta":beta,"seed":seed,
        "sft_train_nll_initial":round(before_sft,5),
        "sft_train_nll_final":round(after_sft,5),
        "validation_preference_margin_before_dpo":round(before_dpo,5),
        "validation_preference_margin_after_dpo":round(after_dpo,5),
        "last_dpo_train_loss":round(losses[-1],5),
        "warning":"Toy bigram, severe limitations; margins can fall on validation. Not model quality or real FUNiX work."
    }
    folder=Path(output_dir)
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"toy_posttrained.json").write_text(
        json.dumps({"architecture":"bigram_causal_lm", "phase":"after_sft_and_dpo",
                    "charset":tok.charset, "weights":policy.weights,
                    "reference_frozen":True},ensure_ascii=True),encoding="utf-8")
    (folder/"metrics.json").write_text(json.dumps(result,indent=2,ensure_ascii=True),encoding="utf-8")
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pretrained",default="artifacts/pretraining/tiny_pretrained.json")
    parser.add_argument("--output-dir",default="artifacts/posttraining")
    parser.add_argument("--sft-epochs",type=int,default=2)
    parser.add_argument("--dpo-epochs",type=int,default=2)
    args=parser.parse_args()
    print(json.dumps(fit(args.pretrained,args.output_dir,
                          args.sft_epochs,args.dpo_epochs),indent=2,ensure_ascii=True))
if __name__=="__main__":
    main()
