"""Offline retrieval benchmark must be stable on bundled demo knowledge base."""
from scripts.evaluate_rag import CASES, evaluate


def test_rag_evaluation_protocol_and_thresholds():
    result = evaluate()
    assert len(CASES) >= 10
    assert result["positive_total"] >= 6
    assert result["no_evidence_total"] >= 3
    assert result["k"] == 3
    assert result["retrieval_recall_at_k"] == 1.0, result["rows"]
    assert result["citation_correctness"] >= 0.9, result["rows"]
    assert result["answer_correctness_proxy"] == 1.0, result["rows"]
    assert result["no_evidence_pass"] == result["no_evidence_total"], result["rows"]


def test_rag_evaluation_reports_out_of_scope_metrics_without_claiming_live_accuracy():
    result = evaluate()
    assert result["citation_total"] >= result["positive_total"]
    assert "No live LLM semantic correctness" in result["limitations"]
    assert all("cited_sources" in row and "answer_correct_proxy" in row for row in result["rows"])
