from rag_engine import KnowledgeBase


def main() -> None:
    kb = KnowledgeBase("knowledge_base")
    print("Knowledge base diagnostic")
    print(f"Documents: {kb.document_count}")
    print(f"Chunks: {kb.chunk_count}")

    if kb.document_count == 0:
        print("WARNING: no Markdown documents found in knowledge_base/")
        return

    sample = kb.search("quy trình issue github", k=3, min_score=0.0)
    print("Sample retrieval:")
    for item in sample:
        print(f"- {item.source}: score={item.score:.4f}")


if __name__ == "__main__":
    main()
