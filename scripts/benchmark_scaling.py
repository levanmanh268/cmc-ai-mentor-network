"""Offline scale sample for retrieval and mentor ranking.

Synthetic data is used to expose growth trends, not to claim production capacity.
Run with ``python -m scripts.benchmark_scaling --output reports/scaling.json``.
"""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
import statistics
import tempfile
import time

import matching_engine
from rag_engine import KnowledgeBase


def _percentile95(samples: list[float]) -> float:
    return sorted(samples)[int((len(samples) - 1) * 0.95)]


def _measure(operation, callback, *, warmups: int, samples: int) -> dict[str, object]:
    for _ in range(warmups):
        callback()
    values = []
    for _ in range(samples):
        start = time.perf_counter()
        result = callback()
        if result is None:
            raise RuntimeError(f"{operation} returned None")
        values.append((time.perf_counter() - start) * 1000)
    return {
        "operation": operation,
        "samples": samples,
        "p50_ms": round(statistics.median(values), 3),
        "p95_ms": round(_percentile95(values), 3),
        "max_ms": round(max(values), 3),
    }


def _mentor(identifier: int) -> dict[str, object]:
    return {
        "id": identifier,
        "name": f"Mentor {identifier}",
        "field": f"AI domain {identifier % 7}",
        "title": "Engineer",
        "bio": f"Supports retrieval, Python, data and project {identifier % 11}",
        "strengths": ["RAG", "Python", f"domain{identifier % 7}"],
        "available_for": ["Career guidance", "Project review"],
        "experience_years": identifier % 12,
    }


def run(*, warmups: int = 10, samples: int = 100) -> dict[str, object]:
    results = []
    with tempfile.TemporaryDirectory(prefix="cmc-rag-scale-") as temp:
        base = Path(temp)
        for count in (3, 30, 100):
            root = base / f"docs-{count}"
            root.mkdir()
            for index in range(count):
                (root / f"guide-{index:04}.md").write_text(
                    f"Guide {index}: RAG retrieval project evidence and citation. "
                    f"Domain marker topic{index % 13} mentor workflow.",
                    encoding="utf-8",
                )
            kb = KnowledgeBase(root)
            results.append({
                "dataset": "markdown_documents",
                "size": count,
                "chunks": kb.chunk_count,
                **_measure("rag_search", lambda: kb.search("RAG retrieval evidence citation", k=4), warmups=warmups, samples=samples),
            })

        original_factory = matching_engine.get_mentor_repository
        profile = {"year": "Năm 2", "field_interest": "AI RAG Python", "goals": "retrieval project", "bio": ""}
        try:
            for count in (10, 100, 500):
                pool = [_mentor(index + 1) for index in range(count)]

                class Repository:
                    def list(self):
                        return pool

                matching_engine.get_mentor_repository = lambda repository=Repository(): repository
                results.append({
                    "dataset": "mentors",
                    "size": count,
                    **_measure("mentor_ranking", lambda: matching_engine.get_top_matches(profile, top_k=3), warmups=warmups, samples=samples),
                })
        finally:
            matching_engine.get_mentor_repository = original_factory

    return {
        "scope": "LOCAL_SYNTHETIC_CPU_ONLY_NOT_CLOUD_OR_CONCURRENCY_SLA",
        "environment": {
            "python": platform.python_version(),
            "os": platform.platform(),
            "processor": platform.processor() or "not reported",
            "warmups": warmups,
        },
        "results": results,
        "limitations": "Synthetic records, warm in-process calls, no network/provider/browser or concurrent load. Compare trends only; no approved SLA threshold.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--warmups", type=int, default=10)
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.warmups < 0 or args.samples < 1:
        parser.error("--warmups must be >= 0 and --samples must be >= 1")
    result = run(warmups=args.warmups, samples=args.samples)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
