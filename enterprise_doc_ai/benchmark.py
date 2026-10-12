"""Reproducible bilingual, access-scoped retrieval and abstention evaluation.

Metrics are not production estimates. Public synthetic test cases are not blind.
No external LLM calls, OCR downloads, model training or GPU usage.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import math
import statistics
import time
from .engine import Principal, EnterpriseIndex, GroundedQA, load_corpus

def load_cases(path: str | Path | None = None) -> list[dict]:
    if path is None:
        path = Path(__file__).parent / "data" / "evaluation.jsonl"
    cases = [json.loads(row) for row in Path(path).read_text(encoding="utf-8").splitlines() if row.strip()]
    if len(set(c["id"] for c in cases)) != len(cases):
        raise ValueError("Duplicate question identifiers")
    return cases

def evaluate(index: EnterpriseIndex, cases: list[dict], method: str = "hybrid", k: int = 3) -> dict:
    if not cases or k < 1:
        raise ValueError("Need cases and k > 0")
    qa = GroundedQA(index)
    answerable, negative, details, latencies = [], [], [], []
    leakages = 0
    unauthorized_version = 0
    for row in cases:
        principal = Principal(row["tenant"], frozenset(row["roles"]), subject="evaluation")
        start = time.perf_counter()
        hits = index.search(row["question"], principal, method=method, k=k, as_of=row["as_of"])
        result = qa.answer(row["question"], principal, method=method, as_of=row["as_of"])
        latencies.append((time.perf_counter() - start) * 1000)
        for hit in hits:
            if not hit.passage.accessible(principal):
                leakages += 1
            if hit.passage.effective > row["as_of"]:
                unauthorized_version += 1
        # Evaluate document family, deduplicating pages in ranking.
        families = list(dict.fromkeys(h.passage.family for h in hits))
        gold = set(row["gold_families"])
        matched_ranks = [i + 1 for i, family in enumerate(families) if family in gold]
        if gold:
            hit = bool(matched_ranks)
            reciprocal_rank = 1 / matched_ranks[0] if hit else 0.0
            gain = sum(1 / math.log2(i + 1) for i in matched_ranks)
            ideal = sum(1 / math.log2(i + 2) for i in range(min(len(gold), k)))
            answerable.append({
                "hit": float(hit), "rr": reciprocal_rank,
                "recall": len(set(families).intersection(gold)) / len(gold),
                "ndcg": gain / ideal if ideal else 0.0,
                "evidence_found": float(result["status"] == "evidence_found"),
            })
        else:
            negative.append({
                "abstained": float(result["status"] == "abstained"),
                "zero_retrieved": float(not hits),
            })
        details.append({
            "id": row["id"], "tag": row["tag"], "split": row["split"],
            "tenant": row["tenant"], "gold_families": sorted(gold),
            "retrieved_families": families, "answer_status": result["status"],
            "source_ids": [h.passage.uid for h in hits],
        })
    avg = lambda key, group: round(statistics.mean(r[key] for r in group), 4) if group else None
    group = defaultdict(list)
    for d in details:
        group[d["tag"]].append(d)
    return {
        "method": method, "k": k, "total_cases": len(cases),
        "answerable_cases": len(answerable), "negative_cases": len(negative),
        "hit_at_k": avg("hit", answerable), "mrr_at_k": avg("rr", answerable),
        "recall_at_k": avg("recall", answerable), "ndcg_at_k": avg("ndcg", answerable),
        "evidence_found_rate_on_answerable": avg("evidence_found", answerable),
        "negative_abstention_rate": avg("abstained", negative),
        "negative_zero_retrieval_rate": avg("zero_retrieved", negative),
        "access_leakage_count": leakages, "future_document_exposure_count": unauthorized_version,
        "latency_ms_median_local": round(statistics.median(latencies), 3),
        "case_counts_by_tag": {tag: len(group[tag]) for tag in sorted(group)},
        "per_case": details,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate frozen, public synthetic corpus. No LLM API.")
    parser.add_argument("--method", choices=["bm25", "char", "hybrid", "all"], default="all")
    parser.add_argument("--split", choices=["dev", "test", "all"], default="test")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    all_cases = load_cases()
    subset = all_cases if args.split == "all" else [q for q in all_cases if q["split"] == args.split]
    index = EnterpriseIndex(load_corpus())
    methods = ["bm25", "char", "hybrid"] if args.method == "all" else [args.method]
    rows = [evaluate(index, subset, method=m, k=args.k) for m in methods]
    artifact = {
        "fixture": "synthetic-public-2026-10-12", "split": args.split, "corpus_passages": len(index.passages),
        "limitations": "Synthetic, openly labelled data; no blind test; not production performance; latency hardware-specific.",
        "metrics": rows,
    }
    output = json.dumps(artifact, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
        print(f"Saved {args.output}")
    for result in rows:
        compact = {k: v for k, v in result.items() if k != "per_case"}
        print(json.dumps(compact, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
