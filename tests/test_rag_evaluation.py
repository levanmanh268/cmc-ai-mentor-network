"""Offline retrieval benchmark must be stable on bundled demo knowledge base."""
from scripts.evaluate_rag import CASES, CASESET_VERSION, evaluate


def test_rag_evaluation_protocol_and_thresholds():
    result = evaluate(warm_repeats=2)
    assert CASESET_VERSION == "nfr-09-v1"
    assert len(CASES) >= 30
    assert result["positive_total"] >= 15
    assert result["no_evidence_total"] >= 10
    assert result["metric_scope"] == "retrieval-hit-at-3-and-no-evidence-refusal-only"
    assert result["positive_hit_at_3"] == result["positive_total"], result["rows"]
    assert result["no_evidence_pass"] == result["no_evidence_total"], result["rows"]
    latency = result["retrieval_latency"]
    assert latency["operation"] == "KnowledgeBase.search(k=3), TF-IDF retrieval only"
    assert latency["first_search_samples"] == len(CASES)
    assert latency["warm_repeats_per_case"] == 2
    assert latency["warm_samples"] == len(CASES) * 2
    assert latency["first_search_p95_ms"] >= latency["first_search_p50_ms"]
    assert latency["warm_p95_ms"] >= latency["warm_p50_ms"]
