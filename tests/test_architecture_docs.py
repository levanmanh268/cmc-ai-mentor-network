"""Architecture documentation regression checks for Windows and Linux."""

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def get_tracked_files():
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [part.decode("utf-8") for part in output.split(b"\0") if part]


def test_no_case_insensitive_filename_collision():
    seen = {}
    for filename in get_tracked_files():
        folded = filename.casefold()
        assert folded not in seen, (
            f"Case-insensitive filename collision: {seen.get(folded)} vs {filename}"
        )
        seen[folded] = filename


def test_one_canonical_architecture_file_and_readme_links():
    filenames = set(get_tracked_files())
    assert "docs/architecture.md" in filenames
    assert "docs/ARCHITECTURE.md" not in filenames
    assert (DOCS / "non-functional-requirements.md").is_file()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "(docs/architecture.md)" in readme
    assert "(docs/non-functional-requirements.md)" in readme
    assert "docs/ARCHITECTURE.md" not in readme


def test_architecture_matches_existing_modules_and_explicitly_states_gaps():
    doc = (DOCS / "architecture.md").read_text(encoding="utf-8")
    for module in (
        "app.py",
        "llm_client.py",
        "rag_engine.py",
        "matching_engine.py",
        "mentors_data.py",
        "ingest.py",
        "knowledge_base/",
    ):
        assert (ROOT / module).exists(), f"Missing source: {module}"
        assert module in doc, f"Missing in architecture: {module}"
    assert "st.session_state" in doc
    assert "get_mentor_repository()" in doc
    assert "Không triển khai" in doc
    assert "TF-IDF" in doc
    assert "Groq" in doc


def test_all_ten_nfrs_have_one_row_and_acknowledge_unverified_targets():
    content = (DOCS / "non-functional-requirements.md").read_text(encoding="utf-8")
    ids = re.findall(r"\*\*NFR-(\d{2})\*\*\s*\|", content)
    assert ids == [f"{n:02d}" for n in range(1, 11)]
    assert "Chưa xác minh" in content
    assert "Chưa đáp ứng" in content
    assert "P95" in content


def test_mermaid_diagrams_stay_in_conservative_github_compatible_subset():
    """Avoid punctuation-heavy edge labels that differ across Mermaid builds."""
    body = (DOCS / "architecture.md").read_text(encoding="utf-8")
    diagrams = re.findall(r"^[\x60]{3}mermaid\s*\n([\s\S]*?)^[\x60]{3}\s*$", body, re.MULTILINE)
    assert len(diagrams) == 5, f"Expected 5 architecture diagrams, got {len(diagrams)}"
    for index, diagram in enumerate(diagrams):
        expected_header = "flowchart " if index < 3 else "sequenceDiagram"
        assert diagram.strip().startswith(expected_header), f"Diagram {index + 1}: incorrect type"
        assert diagram.isascii(), f"Diagram {index + 1}: keep short ASCII labels for compatibility"
        assert not re.search(r'\|".+?"\|', diagram), (
            f"Diagram {index + 1}: use plain connections and explain rich labels in prose"
        )


def test_readme_architecture_tree_uses_real_newline():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Optional Groq infrastructure\n├── rag_engine.py" in readme
    assert "TF-IDF cosine similarity" in readme
