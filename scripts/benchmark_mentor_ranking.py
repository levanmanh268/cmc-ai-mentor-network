"""Reproducible CPU-only mentor-ranking benchmark on demo and synthetic pools."""
from __future__ import annotations

import json
import os
import platform
from unittest.mock import patch

from matching_engine import get_top_matches
from mentors_data import MentorRepository, RAW_MENTORS
from scripts.final_smoke_audit import measure_cold_and_warm

DEFAULT_POOL_SIZES = (len(RAW_MENTORS), 50, 250, 1000)
WARM_REPEATS = 100

STUDENT_PROFILE = {
    "year": "Năm 2",
    "field_interest": "LLM RAG",
    "goals": "Học xây dựng dự án AI",
    "bio": "",
}


def build_benchmark_mentors(size: int) -> list[dict]:
    """Expand fictional demo templates without presenting them as real mentors."""
    if size < 1:
        raise ValueError("size must be at least one")

    mentors = []
    for index in range(size):
        mentor = dict(RAW_MENTORS[index % len(RAW_MENTORS)])
        mentor["id"] = index + 1
        mentor["name"] = f"{mentor['name']} (benchmark {index + 1})"
        mentors.append(mentor)
    return mentors


def benchmark(
    *,
    pool_sizes: tuple[int, ...] = DEFAULT_POOL_SIZES,
    warm_repeats: int = WARM_REPEATS,
) -> dict[str, object]:
    if warm_repeats < 1:
        raise ValueError("warm_repeats must be at least one")
    if not pool_sizes or any(size < 1 for size in pool_sizes):
        raise ValueError("pool_sizes must contain positive sizes")

    results = []
    for pool_size in pool_sizes:
        repository = MentorRepository(build_benchmark_mentors(pool_size))
        with patch("matching_engine.get_mentor_repository", return_value=repository):
            measurements = measure_cold_and_warm(
                f"mentor ranking, pool={pool_size}, top_k=3",
                lambda: get_top_matches(STUDENT_PROFILE, top_k=3),
                n=warm_repeats,
            )
        results.append(
            {
                "pool_size": pool_size,
                "top_k": 3,
                **measurements,
            }
        )

    return {
        "scope": "LOCAL_CPU_ONLY_SYNTHETIC_EXPANSION_NOT_PRODUCTION_OR_SLA",
        "environment": {
            "python": platform.python_version(),
            "system": platform.system(),
            "cpu": platform.processor() or "unknown",
            "logical_cpus": os.cpu_count(),
            "template_mentors": len(RAW_MENTORS),
            "pool_sizes": list(pool_sizes),
            "warm_repeats_per_pool": warm_repeats,
        },
        "results": results,
        "limitations": (
            "Pools larger than the five fictional demo mentors repeat those "
            "templates with unique IDs/names. Cold is the first ranking call "
            "after Python imports and pool construction. No real mentor records, "
            "concurrency, Streamlit/browser, network, LLM or production SLA."
        ),
    }


def main() -> None:
    result = benchmark()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
