from rag_engine import KnowledgeBase
from matching_engine import get_top_matches


def test_repository_knowledge_base_loads():
    kb = KnowledgeBase("knowledge_base")

    assert kb.document_count >= 3
    assert kb.chunk_count >= 3


def test_repository_matching_smoke():
    results = get_top_matches(
        {
            "year": "Năm 1",
            "field_interest": "LLM, RAG",
            "goals": "Làm chatbot AI",
            "bio": "",
        },
        top_k=3,
    )

    assert len(results) == 3
    assert results[0]["hybrid_score"] >= results[-1]["hybrid_score"]
