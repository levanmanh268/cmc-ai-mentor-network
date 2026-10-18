"""Reproducible CPU-only classroom latency sample; not an AI/SLA benchmark.

No keys or network calls. Record medians/p95 without assuming a hard SLA.
"""
from __future__ import annotations

import json
import platform
from pathlib import Path
import statistics
import time

from matching_engine import get_top_matches
from rag_engine import KnowledgeBase, answer_with_rag


def _quantile95(values: list[float]) -> float:
    return sorted(values)[int((len(values) - 1) * 0.95)]


def measure(label: str, callback, *, n: int = 50) -> dict[str, float | int | str]:
    durations = []
    for _ in range(n):
        start = time.perf_counter()
        result = callback()
        assert result is not None, f"{label}: operation returned None"
        durations.append((time.perf_counter() - start) * 1000)
    return {
        "operation": label,
        "samples": n,
        "median_ms": round(statistics.median(durations), 3),
        "p95_ms": round(_quantile95(durations), 3),
        "max_ms": round(max(durations), 3),
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    kb = KnowledgeBase(root / "knowledge_base")
    assert kb.document_count >= 1, "Cannot benchmark without demo knowledge base"
    profile = {
        "year": "Năm 2", "field_interest": "LLM RAG",
        "goals": "Học xây dựng dự án AI", "bio": "",
    }
    # Prewarm compiled vectorizer/imports before sampling.
    kb.search("GitHub issue branch commit")
    get_top_matches(profile, top_k=3)

    metrics = [
        measure(
            "offline-rag GitHub question",
            lambda: answer_with_rag("GitHub issue branch commit", kb, client=None),
        ),
        measure(
            "offline-rag out-of-domain refusal",
            lambda: answer_with_rag("công thức quang hợp thực vật", kb, client=None),
        ),
        measure(
            "mentor ranking demo data",
            lambda: get_top_matches(profile, top_k=3),
        ),
    ]
    print(json.dumps({
        "scope": "LOCAL_CPU_ONLY_NOT_PUBLIC_CLOUD_AND_NOT_LLM",
        "environment": {
            "python": platform.python_version(),
            "system": platform.system(),
            "docs": kb.document_count,
            "chunks": kb.chunk_count,
        },
        "results": metrics,
        "limitations": "No browser/network/provider latency; no load/concurrency/SLA claim.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
