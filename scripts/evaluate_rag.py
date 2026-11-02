"""Reproducible small offline TF-IDF retrieval smoke benchmark (not model accuracy)."""
from __future__ import annotations

import math
from pathlib import Path
import statistics
import time

from rag_engine import KnowledgeBase, answer_with_rag

ROOT = Path(__file__).resolve().parents[1]
LATENCY_REPEATS = 100

# Synthetic prompts tailored to the three public demo knowledge-base documents.
# This regression fixture is not independently reviewed or held out.
CASESET_VERSION = "nfr-09-v1"
CASES = (
    ("Issue mô tả vấn đề và tiêu chí hoàn thành", "ai_project_guide.md"),
    ("Tạo branch riêng từ main", "ai_project_guide.md"),
    ("Pull Request dùng Closes issue-number", "ai_project_guide.md"),
    ("debug kiểm tra ingestion retrieval prompt model", "ai_study_guide.md"),
    ("RAG tách bước truy xuất tài liệu liên quan và sinh câu trả lời", "ai_project_guide.md"),
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


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]


def evaluate(
    root: Path = ROOT / "knowledge_base",
    *,
    warm_repeats: int = LATENCY_REPEATS,
) -> dict[str, object]:
    if warm_repeats < 1:
        raise ValueError("warm_repeats must be at least one")
    kb = KnowledgeBase(root)
    rows: list[dict[str, object]] = []
    first_search_ms: list[float] = []
    warm_search_ms: list[float] = []
    for query, expected in CASES:
        start = time.perf_counter()
        hits = kb.search(query, k=3)
        first_search_ms.append((time.perf_counter() - start) * 1000)

        for _ in range(warm_repeats):
            start = time.perf_counter()
            kb.search(query, k=3)
            warm_search_ms.append((time.perf_counter() - start) * 1000)

        response = answer_with_rag(query, kb, client=None)
        success = (
            expected in [chunk.source for chunk in hits]
            if expected is not None
            else not hits and response.mode == "no-evidence"
        )
        rows.append(
            {
                "query": query,
                "expected": expected or "NO_EVIDENCE",
                "top3": [chunk.source for chunk in hits],
                "mode": response.mode,
                "pass": bool(success),
            }
        )
    positives = [r for r in rows if r["expected"] != "NO_EVIDENCE"]
    negatives = [r for r in rows if r["expected"] == "NO_EVIDENCE"]
    return {
        "caseset_version": CASESET_VERSION,
        "metric_scope": "retrieval-hit-at-3-and-no-evidence-refusal-only",
        "positive_hit_at_3": sum(bool(x["pass"]) for x in positives),
        "positive_total": len(positives),
        "no_evidence_pass": sum(bool(x["pass"]) for x in negatives),
        "no_evidence_total": len(negatives),
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
    }


def main() -> int:
    result = evaluate()
    for row in result["rows"]:
        print(f"{'PASS' if row['pass'] else 'FAIL'} | {row['expected']} | {row['query']} | {row['mode']} | {row['top3']}")
    print(
        f"Hit@3: {result['positive_hit_at_3']}/{result['positive_total']}; "
        f"No-evidence: {result['no_evidence_pass']}/{result['no_evidence_total']}"
    )
    latency = result["retrieval_latency"]
    print(
        "Retrieval latency (TF-IDF search only): "
        f"first-search p50/p95={latency['first_search_p50_ms']}/"
        f"{latency['first_search_p95_ms']} ms; "
        f"warm p50/p95={latency['warm_p50_ms']}/"
        f"{latency['warm_p95_ms']} ms "
        f"({latency['warm_samples']} samples)"
    )
    return 0 if all(x["pass"] for x in result["rows"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
