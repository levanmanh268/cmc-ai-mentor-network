"""Offline RAG retrieval, citation-mapping, evidence-proxy, and latency evaluation."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
import statistics
import time

from rag_engine import KnowledgeBase, answer_with_rag

ROOT = Path(__file__).resolve().parents[1]
CASESET_VERSION = "nfr-09-v2"
LATENCY_REPEATS = 100

# Synthetic, in-sample prompts against the three bundled demo documents.
# They are not an independent gold set or a general LLM accuracy benchmark.
CASES = (
    ("Issue mô tả vấn đề và tiêu chí hoàn thành", "ai_project_guide.md"),
    ("Tạo branch riêng từ main", "ai_project_guide.md"),
    ("Pull Request dùng Closes issue-number", "ai_project_guide.md"),
    ("debug kiểm tra ingestion retrieval prompt model", "ai_study_guide.md"),
    ("RAG tách bước truy xuất tài liệu liên quan và sinh câu trả lời", ("ai_project_guide.md", "ai_study_guide.md")),
    ("API key chưa cấu hình API mất kết nối và input rỗng", "ai_project_guide.md"),
    ("Câu hỏi có bằng chứng câu không bằng chứng và gây nhiễu", "ai_study_guide.md"),
    ("Metric đánh giá baseline trước tối ưu mô hình", "ai_study_guide.md"),
    ("Kiểm tra indexing query strategy khi retrieval sai", "ai_study_guide.md"),
    ("Giảm hallucination bằng temperature context citation threshold", "ai_study_guide.md"),
    ("Tách tầng ingestion retrieval prompt model generation", "ai_study_guide.md"),
    ("Tạo tập câu hỏi kiểm thử gồm positive negative và nhiễu", "ai_study_guide.md"),
    ("Mentor profile năm học lĩnh vực quan tâm mục tiêu giới thiệu ngắn", "mentor_matching.md"),
    ("Matching kết hợp độ tương đồng nội dung và quy tắc giải thích", "mentor_matching.md"),
    ("Sinh viên năm đầu thêm điểm khi mentor nhiều năm kinh nghiệm", "mentor_matching.md"),
    ("So sánh lĩnh vực quan tâm với field và strengths của mentor", "mentor_matching.md"),
    ("LLM không khả dụng vẫn deterministic ranking và explanation", "mentor_matching.md"),
    ("Đọc bio strengths và mục tiêu của mentor trước khi liên hệ", "mentor_matching.md"),
    ("Chlorophyll quang hợp lá cây quang năng", None),
    ("Đường bay sao Hỏa của tàu vũ trụ", None),
    ("Công thức nấu bún bò Huế và rau thơm", None),
    ("Lịch thi đấu môn bóng đá World Cup", None),
    ("Thuế nhập khẩu cá hồi Bắc Âu", None),
    ("Hydrology watershed rainfall aquifer glaciology", None),
    ("Macroeconomic inflation bond yields central bank", None),
    ("Pharmacology dosage contraindication antibiotic", None),
    ("Geology basalt magma tectonic subduction", None),
    ("Knitting crochet yarn cardigan needle", None),
    ("Classical guitar tablature concerto orchestration", None),
    ("Volcanology ash plume lava caldera", None),
    ("Fisheries salmon migration hatchery", None),
)

EXPECTED_TERMS = {
    CASES[0][0]: ("issue", "tiêu chí hoàn thành"),
    CASES[1][0]: ("branch", "main"),
    CASES[2][0]: ("pull request", "closes"),
    CASES[3][0]: ("ingestion", "retrieval", "prompt", "model generation"),
    CASES[4][0]: ("truy xuất tài liệu liên quan", "sinh câu trả lời"),
    CASES[5][0]: ("api key", "mất kết nối", "input rỗng"),
    CASES[6][0]: ("bằng chứng", "gây nhiễu"),
    CASES[7][0]: ("metric", "baseline"),
    CASES[8][0]: ("indexing", "query strategy"),
    CASES[9][0]: ("hallucination", "temperature", "citation", "threshold"),
    CASES[10][0]: ("ingestion", "retrieval", "prompt", "model generation"),
    CASES[11][0]: ("tập câu hỏi", "bằng chứng", "gây nhiễu"),
    CASES[12][0]: ("năm học", "lĩnh vực quan tâm", "mục tiêu"),
    CASES[13][0]: ("độ tương đồng", "quy tắc"),
    CASES[14][0]: ("năm đầu", "nhiều năm kinh nghiệm"),
    CASES[15][0]: ("lĩnh vực", "strengths"),
    CASES[16][0]: ("llm", "ranking", "deterministic"),
    CASES[17][0]: ("bio", "strengths", "mục tiêu"),
}


def _score_citations(
    *,
    expected_sources: list[str],
    retrieved_sources: list[str],
    cited_ids: list[int],
    cited_sources: list[str],
) -> tuple[bool, int, int]:
    """Score source mapping independently from semantic entailment.

    A positive case passes when every citation ID maps to a source in the
    retrieved top-k and every expected source is cited. Multiple expected
    sources are supported; the metric does not judge whether every cited
    passage entails a generated claim.
    """
    valid_mapping = (
        len(cited_sources) == len(cited_ids)
        and all(source in retrieved_sources for source in cited_sources)
    )
    case_pass = (
        bool(cited_ids)
        and valid_mapping
        and set(expected_sources).issubset(cited_sources)
    )
    correct_citations = sum(source in retrieved_sources for source in cited_sources)
    return case_pass, correct_citations, len(cited_ids)


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]


def evaluate(
    root: Path = ROOT / "knowledge_base",
    *,
    k: int = 3,
    warm_repeats: int = 2,
) -> dict[str, object]:
    if k < 1:
        raise ValueError("k must be at least one")
    if warm_repeats < 1:
        raise ValueError("warm_repeats must be at least one")

    kb = KnowledgeBase(root)
    rows: list[dict[str, object]] = []
    first_search_ms: list[float] = []
    warm_search_ms: list[float] = []
    relevant_total = relevant_hits = 0
    citation_total = citation_correct = 0
    answer_total = answer_correct = 0
    no_evidence_total = no_evidence_pass = 0

    for query, expected in CASES:
        expected_sources = (
            []
            if expected is None
            else [expected]
            if isinstance(expected, str)
            else list(expected)
        )
        start = time.perf_counter()
        hits = kb.search(query, k=k)
        first_search_ms.append((time.perf_counter() - start) * 1000)
        for _ in range(warm_repeats):
            start = time.perf_counter()
            kb.search(query, k=k)
            warm_search_ms.append((time.perf_counter() - start) * 1000)

        response = answer_with_rag(query, kb, client=None)
        retrieved_sources = [chunk.source for chunk in hits]
        cited_ids = [int(value) for value in re.findall(r"\[S(\d+)\]", response.answer)]
        cited_sources = [
            response.sources[index - 1].source
            for index in cited_ids
            if 1 <= index <= len(response.sources)
        ]
        if expected_sources:
            relevant_total += 1
            source_hit = all(source in retrieved_sources for source in expected_sources)
            relevant_hits += int(source_hit)
            citation_ok, correct_count, total_count = _score_citations(
                expected_sources=expected_sources,
                retrieved_sources=retrieved_sources,
                cited_ids=cited_ids,
                cited_sources=cited_sources,
            )
            citation_total += total_count
            citation_correct += correct_count

            expected_terms = EXPECTED_TERMS[query]
            cited_text = " ".join(
                chunk.text.lower()
                for chunk in response.sources
                if chunk.source in cited_sources
            )
            terms_found = [term for term in expected_terms if term.lower() in cited_text]
            answer_ok = len(terms_found) == len(expected_terms)
            answer_total += 1
            answer_correct += int(answer_ok)
            success = source_hit and citation_ok and answer_ok
        else:
            no_evidence_total += 1
            citation_ok = not hits and not cited_ids and response.mode == "no-evidence"
            no_evidence_pass += int(citation_ok)
            terms_found = []
            expected_terms = ()
            answer_ok = citation_ok
            success = citation_ok
            citation_total += len(cited_ids)

        rows.append({
            "query": query,
            "expected": expected_sources or "NO_EVIDENCE",
            "top_k": retrieved_sources,
            "cited_sources": cited_sources,
            "mode": response.mode,
            "citation_correct": citation_ok,
            "expected_answer_terms": list(expected_terms),
            "answer_terms_found": terms_found,
            "answer_correct_proxy": answer_ok,
            "pass": bool(success),
        })

    return {
        "caseset_version": CASESET_VERSION,
        "k": k,
        "metric_scope": "retrieval-citation-answer-evidence-proxy-and-no-evidence-refusal",
        "positive_hit_at_k": relevant_hits,
        "positive_hit_at_3": relevant_hits,
        "positive_total": relevant_total,
        "retrieval_recall_at_k": round(relevant_hits / relevant_total, 4) if relevant_total else 0.0,
        "citation_correct": citation_correct,
        "citation_total": citation_total,
        "citation_correctness": round(citation_correct / citation_total, 4) if citation_total else 0.0,
        "answer_correct_proxy": answer_correct,
        "answer_total": answer_total,
        "answer_correctness_proxy": round(answer_correct / answer_total, 4) if answer_total else 0.0,
        "no_evidence_pass": no_evidence_pass,
        "no_evidence_total": no_evidence_total,
        "retrieval_latency": {
            "operation": "KnowledgeBase.search(k=3), TF-IDF retrieval only",
            "cases": len(CASES),
            "first_search_samples": len(first_search_ms),
            "first_search_p50_ms": round(statistics.median(first_search_ms), 3),
            "first_search_p95_ms": round(_percentile(first_search_ms, 0.95), 3),
            "warm_repeats_per_case": warm_repeats,
            "warm_samples": len(warm_search_ms),
            "warm_p50_ms": round(statistics.median(warm_search_ms), 3),
            "warm_p95_ms": round(_percentile(warm_search_ms, 0.95), 3),
        },
        "rows": rows,
        "limitations": "Small in-sample demo corpus; answer correctness is an evidence-term proxy. No live LLM semantic correctness or claim-level entailment is measured.",
    }


def main() -> int:
    result = evaluate(warm_repeats=LATENCY_REPEATS)
    for row in result["rows"]:
        print(json.dumps({"status": "PASS" if row["pass"] else "FAIL", **row}, ensure_ascii=True))
    print(f"Recall@{result['k']}: {result['positive_hit_at_k']}/{result['positive_total']} ({result['retrieval_recall_at_k']:.0%})")
    print(f"Citation correctness: {result['citation_correct']}/{result['citation_total']} ({result['citation_correctness']:.0%})")
    print(f"Answer correctness proxy: {result['answer_correct_proxy']}/{result['answer_total']} ({result['answer_correctness_proxy']:.0%})")
    print(f"No-evidence refusal: {result['no_evidence_pass']}/{result['no_evidence_total']}")
    latency = result["retrieval_latency"]
    print(f"Retrieval latency first-search p50/p95: {latency['first_search_p50_ms']}/{latency['first_search_p95_ms']} ms")
    print(f"Retrieval latency warm p50/p95: {latency['warm_p50_ms']}/{latency['warm_p95_ms']} ms ({latency['warm_samples']} samples)")
    print(f"Limitations: {result['limitations']}")
    return 0 if all(row["pass"] for row in result["rows"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
