"""Reproducible retrieval evaluation: hit@k, MRR@k, nDCG@k and latency."""
import argparse
import json
import math
import statistics
import time
from pathlib import Path
from .core import BM25Index, TFIDFIndex, Document, chunk_text

def load_corpus(folder: str | Path) -> list[Document]:
    docs = []
    for path in sorted(Path(folder).glob("*.md")):
        docs.extend(chunk_text(path.read_text(encoding="utf-8"), path.name, size=150, overlap=20))
    return docs

def evaluate(index, cases: list[dict], k: int = 3) -> dict:
    if not cases or k < 1:
        raise ValueError("Need nonempty cases and k >= 1")
    hit_scores, rr_scores, ndcg_scores, latencies, negative_ok = [], [], [], [], []
    details = []
    for case in cases:
        start = time.perf_counter()
        hits = index.search(case["question"], k)
        latencies.append((time.perf_counter() - start) * 1000)
        ranked = [h.document.id.split("#")[0] for h in hits]
        relevant = set(case["relevant_sources"])
        positions = [rank + 1 for rank, source in enumerate(ranked) if source in relevant]
        hit = bool(positions)
        if relevant:
            hit_scores.append(float(hit))
            rr_scores.append(1 / min(positions) if positions else 0.0)
            dcg = sum(1 / math.log2(i + 1) for i in positions)
            ideal = sum(1 / math.log2(i + 2) for i in range(min(k, len(relevant))))
            ndcg_scores.append(dcg / ideal)
        else:
            negative_ok.append(float(not hits))
        details.append({"id": case["id"], "expected": sorted(relevant), "retrieved": ranked, "hit": hit})
    return {
        "count": len(cases), "answerable_cases": len(hit_scores), "negative_cases": len(negative_ok), "k": k,
        "hit_at_k": round(statistics.mean(hit_scores), 4) if hit_scores else None,
        "mrr_at_k": round(statistics.mean(rr_scores), 4) if rr_scores else None,
        "ndcg_at_k": round(statistics.mean(ndcg_scores), 4) if ndcg_scores else None,
        "negative_abstention_accuracy": round(statistics.mean(negative_ok), 4) if negative_ok else None,
        "latency_ms_median": round(statistics.median(latencies), 3),
        "per_case": details,
    }

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--method", choices=["bm25", "tfidf"], default="bm25")
    p.add_argument("--k", type=int, default=3)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    base = Path(__file__).resolve().parent
    docs = load_corpus(base / "data" / "knowledge")
    cases = [json.loads(line) for line in (base / "data" / "eval.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    index = BM25Index(docs) if args.method == "bm25" else TFIDFIndex(docs)
    result = {"method": args.method, "corpus_documents": len(docs), **evaluate(index, cases, args.k)}
    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)

if __name__ == "__main__":
    main()
