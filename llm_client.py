from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


def get_groq_api_key() -> str:
    """Read the Groq credential from the process environment."""
    return os.getenv("GROQ_API_KEY", "").strip()


def llm_enabled() -> bool:
    """Return whether an online LLM credential is configured."""
    return bool(get_groq_api_key())


def build_llm_client() -> Any | None:
    """Create the external LLM client at the infrastructure boundary."""
    api_key = get_groq_api_key()
    if not api_key:
        return None
    return Groq(api_key=api_key)
