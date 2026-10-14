"""Reproducible small offline TF-IDF retrieval smoke benchmark (not model accuracy)."""
from __future__ import annotations

from pathlib import Path

from rag_engine import KnowledgeBase, answer_with_rag

ROOT = Path(__file__).resolve().parents[1]

# Synthetic prompts tailored to the three public demo knowledge-base documents.
# No separate held-out test data; results do not generalize to unseen topics.
CASES = (
    ("Issue và Pull Request sau commit?", "ai_project_guide.md"),
    ("Branch riêng và Refs issue-number", "ai_project_guide.md"),
    ("Review CI trước khi merge", "ai_project_guide.md"),
    ("Metric đánh giá baseline trước tối ưu mô hình", "ai_study_guide.md"),
    ("Debug ingestion retrieval prompt model", "ai_study_guide.md"),
    ("Temperature, citation và threshold giảm hallucination", "ai_study_guide.md"),
    ("Hồ sơ sinh viên dùng cho mentor matching", "mentor_matching.md"),
    ("Strengths và field của mentor", "mentor_matching.md"),
    ("Ranking mentor khi LLM không khả dụng", "mentor_matching.md"),
    ("Chlorophyll quang hợp lá cây quang năng", None),
    ("Đường bay sao Hỏa của tàu vũ trụ", None),
    ("Công thức nấu bún bò Huế và rau thơm", None),
    ("Lịch thi đấu môn bóng đá World Cup", None),
    ("Thuế nhập khẩu cá hồi Bắc Âu", None),
)


def evaluate(root: Path = ROOT / "knowledge_base") -> dict[str, object]:
    kb = KnowledgeBase(root)
    rows: list[dict[str, object]] = []
    for query, expected in CASES:
        hits = kb.search(query, k=3)
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
        "positive_hit_at_3": sum(bool(x["pass"]) for x in positives),
        "positive_total": len(positives),
        "no_evidence_pass": sum(bool(x["pass"]) for x in negatives),
        "no_evidence_total": len(negatives),
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
    return 0 if all(x["pass"] for x in result["rows"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
