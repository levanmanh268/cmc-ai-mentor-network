from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


def get_groq_api_key(override: str | None = None) -> str:
    """Resolve a session override or the process secret, never log credentials."""
    key = (os.getenv("GROQ_API_KEY", "") if override is None else override).strip()
    if key.lower() in {
        "", "your_groq_api_key_here", "your_api_key_here",
        "replace_with_your_api_key", "change_me", "changeme",
    }:
        return ""
    return key


def llm_enabled() -> bool:
    """Return whether an online LLM credential is configured."""
    return bool(get_groq_api_key())


def build_llm_client(api_key: str | None = None) -> Any | None:
    """Construct a Groq client using either a session-only or server credential."""
    api_key = get_groq_api_key(api_key)
    if not api_key:
        return None
    return Groq(api_key=api_key, timeout=35.0, max_retries=1)
