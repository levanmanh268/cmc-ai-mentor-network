"""Reproducible CPU-only classroom latency sample; not an AI/SLA benchmark.

No keys or network calls. Record medians/p95 without assuming a hard SLA.
"""
from __future__ import annotations

import json
import math
import os
import platform
from pathlib import Path
import statistics
import time

from matching_engine import get_top_matches
from rag_engine import KnowledgeBase, answer_with_rag


def _quantile95(values: list[float]) -> float:
    if not values:
        raise ValueError("values must not be empty")
    return sorted(values)[math.ceil(0.95 * len(values)) - 1]


def _total_memory_bytes() -> int | None:
    if platform.system() == "Windows":
        import ctypes
        from ctypes import wintypes

        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", wintypes.DWORD),
                ("dwMemoryLoad", wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return int(status.ullTotalPhys)
        return None
    if hasattr(os, "sysconf"):
        try:
            return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
        except (OSError, ValueError):
            return None
    return None


def measure(label: str, callback, *, n: int = 100) -> dict[str, float | int | str]:
    if n < 1:
        raise ValueError("n must be at least one")
    durations = []
    for _ in range(n):
        start = time.perf_counter()
        result = callback()
        assert result is not None, f"{label}: operation returned None"
        durations.append((time.perf_counter() - start) * 1000)
    return {
        "operation": label,
        "samples": n,
        "p50_ms": round(statistics.median(durations), 3),
        "p95_ms": round(_quantile95(durations), 3),
        "max_ms": round(max(durations), 3),
    }


def measure_cold_and_warm(
    label: str, callback, *, n: int = 100, warmups: int = 0
) -> dict[str, object]:
    if warmups < 0:
        raise ValueError("warmups cannot be negative")
    start = time.perf_counter()
    result = callback()
    assert result is not None, f"{label}: cold operation returned None"
    cold_ms = (time.perf_counter() - start) * 1000
    for _ in range(warmups):
        result = callback()
        assert result is not None, f"{label}: warmup operation returned None"
    return {
        "operation": label,
        "cold_ms": round(cold_ms, 3),
        "warmups_excluded": warmups,
        "warm": measure(label, callback, n=n),
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    kb = KnowledgeBase(root / "knowledge_base")
    assert kb.document_count >= 1, "Cannot benchmark without demo knowledge base"
    profile = {
        "year": "Năm 2", "field_interest": "LLM RAG",
        "goals": "Học xây dựng dự án AI", "bio": "",
    }
    metrics = [
        measure_cold_and_warm(
            "offline-rag GitHub question",
            lambda: answer_with_rag("GitHub issue branch commit", kb, client=None),
            warmups=10,
        ),
        measure_cold_and_warm(
            "offline-rag out-of-domain refusal",
            lambda: answer_with_rag("công thức quang hợp thực vật", kb, client=None),
            warmups=10,
        ),
        measure_cold_and_warm(
            "mentor ranking demo data",
            lambda: get_top_matches(profile, top_k=3),
            warmups=10,
        ),
    ]
    print(json.dumps({
        "scope": "LOCAL_CPU_ONLY_NOT_PUBLIC_CLOUD_AND_NOT_LLM",
        "environment": {
            "python": platform.python_version(),
            "system": platform.system(),
            "cpu": platform.processor() or "unknown",
            "logical_cpus": os.cpu_count(),
            "total_memory_bytes": _total_memory_bytes(),
            "docs": kb.document_count,
            "chunks": kb.chunk_count,
        },
        "results": metrics,
        "limitations": "Cold is first operation after imports and knowledge-base loading. Warm timings exclude 10 warmup calls. No browser/network/provider latency; no load/concurrency/SLA claim.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
