"""The mentor ranking benchmark uses bounded, deterministic synthetic inputs."""
import pytest

from scripts.benchmark_mentor_ranking import (
    benchmark,
    build_benchmark_mentors,
)


def test_synthetic_pool_has_unique_ids_and_preserves_mentor_schema():
    mentors = build_benchmark_mentors(12)

    assert len(mentors) == 12
    assert len({mentor["id"] for mentor in mentors}) == 12
    assert all(
        {"id", "name", "title", "company", "field", "experience_years",
         "bio", "strengths", "available_for"} <= mentor.keys()
        for mentor in mentors
    )


@pytest.mark.parametrize("size", [0, -1])
def test_synthetic_pool_rejects_non_positive_sizes(size):
    with pytest.raises(ValueError, match="size must be at least one"):
        build_benchmark_mentors(size)


def test_benchmark_reports_cold_and_warm_samples_for_each_pool():
    result = benchmark(pool_sizes=(5, 12), warm_repeats=2)

    assert result["environment"]["pool_sizes"] == [5, 12]
    assert result["environment"]["warm_repeats_per_pool"] == 2
    assert "SYNTHETIC_EXPANSION" in result["scope"]
    assert [row["pool_size"] for row in result["results"]] == [5, 12]
    assert all(row["top_k"] == 3 for row in result["results"])
    assert all(row["warm"]["samples"] == 2 for row in result["results"])
    assert all(row["cold_ms"] >= 0 for row in result["results"])
    assert all(row["warm"]["p95_ms"] >= row["warm"]["p50_ms"] for row in result["results"])


def test_benchmark_rejects_invalid_sample_configuration():
    with pytest.raises(ValueError, match="warm_repeats"):
        benchmark(pool_sizes=(5,), warm_repeats=0)
    with pytest.raises(ValueError, match="pool_sizes"):
        benchmark(pool_sizes=())
