from scripts.benchmark_scaling import run


def test_scale_benchmark_covers_document_and_mentor_growth():
    result = run(warmups=0, samples=1)

    rag_sizes = [row["size"] for row in result["results"] if row["dataset"] == "markdown_documents"]
    mentor_sizes = [row["size"] for row in result["results"] if row["dataset"] == "mentors"]
    assert rag_sizes == [3, 30, 100]
    assert mentor_sizes == [10, 100, 500]
    assert all(row["p95_ms"] >= 0 for row in result["results"])
    assert "SYNTHETIC" in result["scope"]
