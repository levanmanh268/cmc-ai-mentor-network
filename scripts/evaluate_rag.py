"""Reproducible small offline TF-IDF retrieval smoke benchmark (not model accuracy)."""
from __future__ import annotations

import re
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

# Expected facts are deliberately short phrases present in the retrieved demo
# corpus. This measures evidence retention in the offline excerpt, not the
# semantic correctness of a live model-generated answer.
EXPECTED_TERMS = {
    CASES[0][0]: ("issue", "pull request"),
    CASES[1][0]: ("branch", "issue"),
    CASES[2][0]: ("review", "ci"),
    CASES[3][0]: ("metric", "baseline"),
    CASES[4][0]: ("debug", "retrieval"),
    CASES[5][0]: ("temperature", "citation"),
    CASES[6][0]: ("hồ sơ", "mentor matching"),
    CASES[7][0]: ("strengths", "field"),
    CASES[8][0]: ("ranking", "llm"),
}


def evaluate(root: Path = ROOT / "knowledge_base", *, k: int = 3) -> dict[str, object]:
    kb = KnowledgeBase(root)
    rows: list[dict[str, object]] = []
    relevant_source_count = 0
    relevant_source_hits = 0
    citation_count = 0
    correct_citation_count = 0
    answer_count = 0
    correct_answer_count = 0
    negative_count = 0
    correct_negative_count = 0
    for query, expected in CASES:
        hits = kb.search(query, k=k)
        response = answer_with_rag(query, kb, client=None)
        retrieved_sources = [chunk.source for chunk in hits]
        if expected is not None:
            relevant_source_count += 1
            source_hit = expected in retrieved_sources
            relevant_source_hits += int(source_hit)
            cited_ids = [int(value) for value in re.findall(r"\[S(\d+)\]", response.answer)]
            cited_sources = [
                response.sources[index - 1].source
                for index in cited_ids
                if 1 <= index <= len(response.sources)
            ]
            citation_ok = bool(cited_ids) and len(cited_sources) == len(cited_ids) and all(
                source == expected for source in cited_sources
            )
            citation_count += len(cited_ids)
            correct_citation_count += sum(source == expected for source in cited_sources)

            expected_terms = EXPECTED_TERMS.get(query, ())
            cited_text = " ".join(
                chunk.text.lower()
                for chunk in response.sources
                if chunk.source in cited_sources
            )
            terms_found = [term for term in expected_terms if term.lower() in cited_text]
            answer_ok = bool(expected_terms) and len(terms_found) == len(expected_terms)
            answer_count += int(bool(expected_terms))
            correct_answer_count += int(answer_ok)
            success = source_hit and citation_ok and answer_ok
        else:
            negative_count += 1
            cited_ids = [int(value) for value in re.findall(r"\[S(\d+)\]", response.answer)]
            cited_sources = []
            citation_ok = not hits and not cited_ids and response.mode == "no-evidence"
            answer_ok = citation_ok
            correct_negative_count += int(answer_ok)
            success = answer_ok
        rows.append(
            {
                "query": query,
                "expected": expected or "NO_EVIDENCE",
                "top_k": retrieved_sources,
                "cited_sources": cited_sources,
                "mode": response.mode,
                "citation_correct": citation_ok,
                "expected_answer_terms": list(EXPECTED_TERMS.get(query, ())),
                "answer_terms_found": terms_found if expected is not None else [],
                "answer_correct_proxy": answer_ok,
                "pass": bool(success),
            }
        )
    return {
        "k": k,
        "positive_hit_at_k": relevant_source_hits,
        "positive_total": relevant_source_count,
        "retrieval_recall_at_k": round(relevant_source_hits / relevant_source_count, 4) if relevant_source_count else 0.0,
        "citation_correct": correct_citation_count,
        "citation_total": citation_count,
        "citation_correctness": round(correct_citation_count / citation_count, 4) if citation_count else 0.0,
        "answer_correct_proxy": correct_answer_count,
        "answer_total": answer_count,
        "answer_correctness_proxy": round(correct_answer_count / answer_count, 4) if answer_count else 0.0,
        "no_evidence_pass": correct_negative_count,
        "no_evidence_total": negative_count,
        "rows": rows,
        "limitations": "Small in-sample demo corpus; offline excerpt evidence proxy only. No live LLM semantic correctness or claim-level entailment is measured.",
    }


def main() -> int:
    result = evaluate()
    for row in result["rows"]:
        # JSON escaping keeps the CLI usable on Windows consoles with legacy
        # encodings that cannot represent all Vietnamese characters.
        import json
        print(json.dumps({"status": "PASS" if row["pass"] else "FAIL", **row}, ensure_ascii=True))
    print(f"Recall@{result['k']}: {result['positive_hit_at_k']}/{result['positive_total']} ({result['retrieval_recall_at_k']:.0%})")
    print(f"Citation correctness: {result['citation_correct']}/{result['citation_total']} ({result['citation_correctness']:.0%})")
    print(f"Answer correctness proxy: {result['answer_correct_proxy']}/{result['answer_total']} ({result['answer_correctness_proxy']:.0%})")
    print(f"No-evidence refusal: {result['no_evidence_pass']}/{result['no_evidence_total']}")
    print(f"Limitations: {result['limitations']}")
    return 0 if all(x["pass"] for x in result["rows"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
