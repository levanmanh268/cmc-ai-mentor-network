"""Actual pre-training of a tiny autoregressive character BIGRAM model.

Pure Python/CPU, no pretrained weights, GPU, external data or API calls.
A bigram is intentionally much weaker than a Transformer; never market as an LLM.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import random

SPECIAL = ("<bos>", "<eos>", "<unk>")

def read_corpus(path=None):
    src = Path(path) if path else Path(__file__).parent / "data" / "corpus.jsonl"
    if not src.is_file() or src.is_symlink() or src.stat().st_size > 1_000_000:
        raise ValueError("Unsafe or missing corpus")
    docs = [json.loads(line) for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids, contents, splits = set(), set(), set()
    for doc in docs:
        if not isinstance(doc, dict) or set(doc) != {"id", "split", "text"}:
            raise ValueError("Invalid document schema")
        if not isinstance(doc["id"], str) or doc["id"] in ids or not doc["id"]:
            raise ValueError("Duplicate or missing document id")
        if doc["split"] not in ("train", "val", "test"):
            raise ValueError("Invalid split")
        if not isinstance(doc["text"], str) or not 25 <= len(doc["text"]) <= 5000:
            raise ValueError("Invalid text")
        normalized = " ".join(doc["text"].casefold().split())
        if normalized in contents:
            raise ValueError("Identical documents across splits")
        ids.add(doc["id"]); contents.add(normalized); splits.add(doc["split"])
    if splits != {"train", "val", "test"}:
        raise ValueError("All train/val/test partitions required")
    return docs

class Tokenizer:
    def __init__(self, charset):
        if any(not isinstance(c, str) or len(c) != 1 for c in charset) or len(set(charset)) != len(charset):
            raise ValueError("Invalid character vocabulary")
        self.charset = sorted(charset)
        self.vocab = {s:i for i,s in enumerate(SPECIAL + tuple(self.charset))}
    @classmethod
    def fit(cls, docs):
        return cls(sorted(set("".join(d["text"] for d in docs if d["split"] == "train"))))
    def encode(self, text, wrap=True):
        seq = [self.vocab.get(c, 2) for c in text]
        return [0] + seq + [1] if wrap else seq
    def decode(self, ids):
        inverse = {v:k for k,v in self.vocab.items()}
        return "".join(inverse.get(i, "<unk>") for i in ids if i >= len(SPECIAL))
    @property
    def size(self):
        return len(self.vocab)

def softmax(row):
    m = max(row)
    z = [math.exp(v-m) for v in row]
    s = sum(z)
    return [v/s for v in z]

class BigramLM:
    def __init__(self, size, seed=42, weights=None):
        if not isinstance(size, int) or not 4 <= size <= 500:
            raise ValueError("Invalid vocab size")
        self.size = size
        if weights is None:
            randomizer = random.Random(seed)
            self.weights = [[randomizer.uniform(-0.01,0.01) for _ in range(size)] for _ in range(size)]
        else:
            if len(weights) != size or any(len(row) != size for row in weights):
                raise ValueError("Wrong weight matrix dimensions")
            if any(not math.isfinite(float(v)) for row in weights for v in row):
                raise ValueError("Nonfinite weights")
            self.weights = [[float(v) for v in row] for row in weights]

    def logprob(self, previous, token):
        if not (0 <= previous < self.size and 0 <= token < self.size):
            raise ValueError("Token out of range")
        return math.log(max(softmax(self.weights[previous])[token], 1e-30))

    def sequence_logprob(self, tokens, start=1):
        """Sum log p(next token | previous) for transitions at indexes >= start."""
        if start < 1 or len(tokens) <= start:
            raise ValueError("Response must contain at least one transition")
        return sum(self.logprob(tokens[i-1], tokens[i]) for i in range(start, len(tokens)))

    def gradient(self, tokens, start=1):
        if start < 1 or len(tokens) <= start:
            raise ValueError("Empty training labels")
        grads = [[0.0] * self.size for _ in range(self.size)]
        for i in range(start, len(tokens)):
            previous, target = tokens[i-1], tokens[i]
            probabilities = softmax(self.weights[previous])
            for j in range(self.size):
                grads[previous][j] += probabilities[j]
            grads[previous][target] -= 1
        return grads

    def step(self, grads, rate):
        if not 0 < rate <= 2:
            raise ValueError("Invalid learning rate")
        for i in range(self.size):
            for j in range(self.size):
                self.weights[i][j] -= rate * grads[i][j]

    def generate(self, prompt, steps=32):
        if not prompt or not 0 <= steps <= 1000:
            raise ValueError("Invalid prompt")
        out = list(prompt)
        for _ in range(steps):
            token = max(range(self.size), key=lambda v: self.weights[out[-1]][v])
            out.append(token)
            if token == 1:
                break
        return out

def transitions(docs, tokenizer, split):
    pairs = []
    for d in docs:
        if d["split"] == split:
            seq = tokenizer.encode(d["text"])
            pairs.extend((seq[i-1], seq[i]) for i in range(1, len(seq)))
    if not pairs:
        raise ValueError("No tokens for split")
    return pairs

def cross_entropy(model, pairs):
    return -sum(model.logprob(a,b) for a,b in pairs) / len(pairs)

def train(output_dir="artifacts/pretraining", epochs=5, learning_rate=0.2, seed=1729):
    if not 1 <= epochs <= 100:
        raise ValueError("Invalid epoch count")
    docs = read_corpus()
    tokenizer = Tokenizer.fit(docs)  # vocabulary fits TRAIN ONLY
    train_pairs = transitions(docs, tokenizer, "train")
    val_pairs = transitions(docs, tokenizer, "val")
    model = BigramLM(tokenizer.size, seed=seed)
    initial = cross_entropy(model, train_pairs)
    randomizer = random.Random(seed)
    for _ in range(epochs):
        randomizer.shuffle(train_pairs)
        for previous, target in train_pairs:
            p = softmax(model.weights[previous])
            gradient = [v - float(i == target) for i,v in enumerate(p)]
            for j in range(model.size):
                model.weights[previous][j] -= learning_rate * gradient[j]
    final = cross_entropy(model, train_pairs)
    valid = cross_entropy(model, val_pairs)
    dataset_hash = hashlib.sha256(
        json.dumps(docs, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    checkpoint = {"objective":"causal_next_character_cross_entropy",
                  "architecture":"bigram_causal_lm", "charset":tokenizer.charset,
                  "weights":model.weights, "seed":seed, "train_corpus_sha256":dataset_hash}
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    (folder/"tiny_pretrained.json").write_text(json.dumps(checkpoint,ensure_ascii=True),encoding="utf-8")
    report = {"architecture":checkpoint["architecture"],"source":"fictional_synthetic_corpus",
              "train_docs":sum(d["split"]=="train" for d in docs),
              "val_docs":sum(d["split"]=="val" for d in docs),
              "test_docs":sum(d["split"]=="test" for d in docs),
              "train_pairs":len(train_pairs),"vocab_size":tokenizer.size,
              "epochs":epochs,"seed":seed,"train_nll_initial":round(initial,5),
              "train_nll_final":round(final,5),"val_nll":round(valid,5),
              "val_perplexity":round(math.exp(min(valid,50)),5),
              "warning":"Not a Transformer, not an enterprise/foundation model, no FUNiX data."}
    (folder/"metrics.json").write_text(json.dumps(report,ensure_ascii=True,indent=2),encoding="utf-8")
    return report

def load_checkpoint(path):
    src = Path(path)
    if src.is_symlink() or not src.is_file() or src.stat().st_size > 2_000_000:
        raise ValueError("Unsafe checkpoint")
    payload = json.loads(src.read_text(encoding="utf-8"))
    if set(payload) != {"objective","architecture","charset","weights","seed","train_corpus_sha256"}:
        raise ValueError("Unexpected checkpoint fields")
    if payload["architecture"] != "bigram_causal_lm":
        raise ValueError("Unsupported checkpoint architecture")
    tokenizer = Tokenizer(payload["charset"])
    model = BigramLM(tokenizer.size, weights=payload["weights"])
    return model, tokenizer, payload

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",default="artifacts/pretraining")
    parser.add_argument("--epochs",type=int,default=5)
    args=parser.parse_args()
    print(json.dumps(train(args.output_dir,epochs=args.epochs),ensure_ascii=True,indent=2))
if __name__=="__main__":
    main()
