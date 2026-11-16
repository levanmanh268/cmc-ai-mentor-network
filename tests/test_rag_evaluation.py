"""Offline retrieval benchmark must be stable on bundled demo knowledge base."""
from scripts.evaluate_rag import CASES, evaluate


def test_rag_evaluation_protocol_and_thresholds():
    result = evaluate()
    assert len(CASES) >= 10
    assert result["positive_total"] >= 6
    assert result["no_evidence_total"] >= 3
    assert result["positive_hit_at_3"] == result["positive_total"], result["rows"]
    assert result["no_evidence_pass"] == result["no_evidence_total"], result["rows"]
