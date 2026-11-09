"""Small, dependency-free security boundaries for the classroom Streamlit app.

Not an identity, authorization, rate-limiting, or session-token subsystem.
"""
from __future__ import annotations

import html
import re
from typing import Any

MAX_RAG_QUESTION_CHARS = 4000


def valid_rag_question(value: Any) -> bool:
    """Reject invalid/oversized input before retrieval or provider calls."""
    return isinstance(value, str) and bool(value.strip()) and len(value) <= MAX_RAG_QUESTION_CHARS


def consented_client(client: Any, consent: bool) -> Any | None:
    """Opt-in must be explicitly True; default and false-like values deny."""
    return client if consent is True else None


def safe_markdown_label(value: Any, *, max_length: int = 500) -> str:
    """Escape untrusted text in an inline Markdown label, not whole content.

    Keep Streamlit unsafe_allow_html=False, as its default.
    """
    raw = "" if value is None else str(value)
    raw = re.sub(r"[\x00-\x1f\x7f]+", " ", raw).strip()[:max(0, max_length)]
    raw = html.escape(raw, quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~\\-])", r"\\\1", raw)
