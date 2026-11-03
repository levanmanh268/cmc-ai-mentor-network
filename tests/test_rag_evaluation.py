"""Offline retrieval benchmark must be stable on bundled demo knowledge base."""
from scripts.evaluate_rag import CASES, CASESET_VERSION, _score_citations, evaluate


def test_all_expected_sources_must_be_cited_for_a_multi_document_case():
    passed, correct, total = _score_citations(
        expected_sources=["guide.md", "study.md"],
        retrieved_sources=["guide.md", "study.md"],
        cited_ids=[1, 2],
        cited_sources=["guide.md", "study.md"],
    )

    assert passed
    assert (correct, total) == (2, 2)


def test_multi_document_case_fails_when_one_expected_source_is_not_cited():
    passed, correct, total = _score_citations(
        expected_sources=["guide.md", "study.md"],
        retrieved_sources=["guide.md", "study.md"],
        cited_ids=[1],
        cited_sources=["guide.md"],
    )

    assert not passed
    assert (correct, total) == (1, 1)


def test_multi_source_citations_pass_when_expected_source_is_in_retrieved_results():
    passed, correct, total = _score_citations(
        expected_source="guide.md",
        retrieved_sources=["guide.md", "study.md"],
        cited_ids=[1, 2],
        cited_sources=["guide.md", "study.md"],
    )

    assert passed
    assert (correct, total) == (2, 2)


def test_multi_source_citations_fail_when_expected_source_is_missing():
    passed, correct, total = _score_citations(
        expected_source="guide.md",
        retrieved_sources=["study.md", "matching.md"],
        cited_ids=[1, 2],
        cited_sources=["study.md", "matching.md"],
    )

    assert not passed
    assert (correct, total) == (2, 2)


def test_citation_with_unresolvable_id_fails_and_counts_as_incorrect():
    passed, correct, total = _score_citations(
        expected_source="guide.md",
        retrieved_sources=["guide.md", "study.md"],
        cited_ids=[1, 99],
        cited_sources=["guide.md"],
    )

    assert not passed
    assert (correct, total) == (1, 2)


def test_citation_to_source_outside_retrieval_fails():
    passed, correct, total = _score_citations(
        expected_source="guide.md",
        retrieved_sources=["guide.md"],
        cited_ids=[1, 2],
        cited_sources=["guide.md", "unretrieved.md"],
    )

    assert not passed
    assert (correct, total) == (1, 2)


def test_case_without_citations_fails_the_positive_citation_requirement():
    passed, correct, total = _score_citations(
        expected_source="guide.md",
        retrieved_sources=["guide.md"],
        cited_ids=[],
        cited_sources=[],
    )

    assert not passed
    assert (correct, total) == (0, 0)


def test_rag_evaluation_protocol_and_thresholds():
    result = evaluate(warm_repeats=2)
    assert CASESET_VERSION == "nfr-09-v1"
    assert len(CASES) >= 30
    assert result["positive_total"] >= 15
    assert result["no_evidence_total"] >= 10
    assert result["metric_scope"] == "retrieval-citation-answer-evidence-proxy-and-no-evidence-refusal"
    assert result["k"] == 3
    assert result["retrieval_recall_at_k"] == 1.0, result["rows"]
    assert result["citation_correctness"] >= 0.9, result["rows"]
    assert result["answer_correctness_proxy"] == 1.0, result["rows"]
    assert result["no_evidence_pass"] == result["no_evidence_total"], result["rows"]
    latency = result["retrieval_latency"]
    assert latency["operation"] == "KnowledgeBase.search(k=3), TF-IDF retrieval only"
    assert latency["first_search_samples"] == len(CASES)
    assert latency["warm_repeats_per_case"] == 2
    assert latency["warm_samples"] == len(CASES) * 2
    assert latency["first_search_p95_ms"] >= latency["first_search_p50_ms"]
    assert latency["warm_p95_ms"] >= latency["warm_p50_ms"]


def test_rag_evaluation_reports_out_of_scope_metrics_without_claiming_live_accuracy():
    result = evaluate()
    assert result["citation_total"] >= result["positive_total"]
    assert "No live LLM semantic correctness" in result["limitations"]
    assert all("cited_sources" in row and "answer_correct_proxy" in row for row in result["rows"])
