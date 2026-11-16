"""Detect likely credentials in repository text/config files.

This is intentionally conservative and focused on high-signal patterns used in
GitHub Actions and cloud provider credentials, so it can run during CI without
printing the secret itself.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

SECRET_PATTERNS = (
    ("Groq-style key", re.compile(r"\bgsk_[A-Za-z0-9]{20,}\b")),
    ("API key-like value", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("PEM private key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
)

PLACEHOLDER_VALUES = {
    "your_groq_api_key_here",
    "your_api_key_here",
    "replace_with_your_api_key",
    "change_me",
    "changeme",
    "example-key",
    "demo-key",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower().strip("'\"` ")
    if not normalized:
        return True
    return normalized in PLACEHOLDER_VALUES or "your_api_key_here" in normalized or "replace_with_your_api_key" in normalized


def _git_tracked_files(root: Path) -> list[Path]:
    try:
        output = subprocess.check_output(["git", "ls-files", "-z"], cwd=root, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    files = []
    for raw in output.decode("utf-8", errors="surrogateescape").split("\0"):
        if not raw:
            continue
        candidate = (root / raw).resolve()
        if candidate.exists() and candidate.is_file():
            files.append(candidate)
    return files


def _iter_repo_files(root: Path) -> list[Path]:
    tracked = _git_tracked_files(root)
    if tracked:
        return tracked

    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        files.append(path)
    return files


def _find_line_matches(line: str) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    if _is_placeholder(line):
        return findings
    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(line):
            candidate = match.group(0)
            if _is_placeholder(candidate):
                continue
            findings.append((label, candidate))
    return findings


def scan_file(path: Path) -> list[dict[str, str | int]]:
    """Return all secret-like hits in a file, with line numbers and redacted snippets."""
    findings: list[dict[str, str | int]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings
    for line_number, line in enumerate(text.splitlines(), start=1):
        matches = _find_line_matches(line)
        if not matches:
            continue
        for label, candidate in matches:
            redacted = line.replace(candidate, "[REDACTED]")
            findings.append({
                "file": str(path),
                "line": line_number,
                "pattern": label,
                "match": candidate,
                "snippet": redacted.strip(),
            })
    return findings


def scan_repository(root: Path) -> list[dict[str, str | int]]:
    findings: list[dict[str, str | int]] = []
    for file in _iter_repo_files(root):
        findings.extend(scan_file(file))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan the repository for likely secret values.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="Repository root to scan")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    findings = scan_repository(root)
    if findings:
        print("Potential secret pattern detected in tracked files:")
        for item in findings:
            print(f"- {item['file']}:{item['line']} [{item['pattern']}] {item['snippet']}")
        print("\nReview and remove or rotate the credential before continuing.")
        return 1

    print(f"No secret pattern detected under {root}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
