"""Regression tests for the reproducible local CPU latency sampler."""
from scripts import final_smoke_audit


def test_measure_reports_nearest_rank_p95_and_sample_count(monkeypatch):
    durations_ms = list(range(1, 21))
    timestamps = []
    current = 0.0
    for duration in durations_ms:
        timestamps.extend((current, current + duration / 1000))
        current += duration / 1000 + 0.001
    values = iter(timestamps)
    monkeypatch.setattr(final_smoke_audit.time, "perf_counter", lambda: next(values))
    calls = []

    def operation():
        calls.append(True)
        return object()

    result = final_smoke_audit.measure("mentor ranking", operation, n=20)

    assert len(calls) == 20
    assert result == {
        "operation": "mentor ranking",
        "samples": 20,
        "p50_ms": 10.5,
        "p95_ms": 19.0,
        "max_ms": 20.0,
    }


def test_cold_and_warm_measurement_runs_one_cold_and_requested_warm_samples():
    calls = []

    def operation():
        calls.append(True)
        return object()

    result = final_smoke_audit.measure_cold_and_warm(
        "mentor ranking", operation, n=3
    )

    assert len(calls) == 4
    assert result["operation"] == "mentor ranking"
    assert result["cold_ms"] >= 0
    assert result["warm"]["samples"] == 3
