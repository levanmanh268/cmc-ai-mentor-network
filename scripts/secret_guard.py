"""Scan tracked files for common accidentally committed credentials."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


SECRET_PATTERNS = (
    re.compile(r"gsk_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
)


def find_secret_patterns(content: str) -> list[str]:
    return [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(content)]


def tracked_files(root: Path) -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    return [root / item.decode("utf-8") for item in output.split(b"\0") if item]


def scan_tracked_files(root: Path) -> list[tuple[Path, int, str]]:
    findings = []
    for path in tracked_files(root):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            for pattern in find_secret_patterns(line):
                findings.append((path.relative_to(root), line_number, pattern))
    return findings


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings = scan_tracked_files(root)
    if findings:
        for path, line_number, pattern in findings:
            print(f"Potential credential pattern {pattern!r} in {path}:{line_number}")
        return 1
    print("No tracked secret pattern detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())