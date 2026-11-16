"""Deterministic handling of *standalone* social utterances in the offline RAG UI.

Never classify arbitrary questions as chit-chat: unrecognized text goes to the
existing RAG pipeline, where evidence requirements still apply.
"""
from __future__ import annotations

import re
import unicodedata


def _normalized_utterance(value: str) -> str:
    """Case/diacritic-insensitive matching; *not* semantic intent detection."""
    text = unicodedata.normalize("NFD", value.casefold().strip())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = text.replace("đ", "d")
    text = re.sub(r"^[\s!?,.;:~❤❤️👋]+|[\s!?,.;:~❤❤️👋]+$", "", text)
    return re.sub(r"\s+", " ", text).strip()


_GREETING = frozenset({
    "hi", "hi cau", "hi ban", "hello", "hello cau", "hello ban",
    "hey", "hey cau", "hey ban", "helo", "helo cau",
    "chao", "chao cau", "chao ban", "xin chao", "xin chao cau",
    "xin chao ban", "chao ai", "chao ad",
})
_THANKS = frozenset({
    "cam on", "cam on cau", "cam on ban", "cam on nhe", "cam on nha",
    "thank you", "thanks", "thanks cau", "thank you cau",
})
_CAPABILITIES = frozenset({
    "ban lam duoc gi", "cau lam duoc gi", "ban co the lam gi",
    "cau co the lam gi", "ban giup duoc gi", "cau giup duoc gi",
    "tro ly nay lam duoc gi", "help", "huong dan su dung",
    "what can you do",
})

_EXAMPLES = (
    "Cậu thử hỏi: **“Quy trình xử lý một Issue GitHub như thế nào?”** "
    "hoặc **“Làm sao giảm hallucination trong RAG?”**"
)


def local_social_reply(message: str) -> str | None:
    """Handle only explicit short social intents, never a general conversation.

    Returns None for anything outside a tight allowlist. Calling this for an
    evidence-bearing question MUST NOT bypass retrieval/citation validation.
    """
    if not isinstance(message, str) or len(message) > 100:
        return None
    utterance = _normalized_utterance(message)
    if utterance in _GREETING:
        return (
            "Chào cậu! 👋 Tớ là trợ lý học tập của CMC AI Mentor Network. "
            "Hiện bản demo chạy **offline**, nên tớ chỉ hỗ trợ chào hỏi cơ bản "
            "và tra cứu những tài liệu đã có, chứ chưa phải chatbot LLM trò chuyện tự do. "
            + _EXAMPLES
        )
    if utterance in _THANKS:
        return (
            "Không có gì đâu cậu! 😊 Nếu muốn tra cứu tài liệu, cậu cứ hỏi nhé. "
            + _EXAMPLES
        )
    if utterance in _CAPABILITIES:
        return (
            "Tớ có thể **truy xuất và trích nguồn từ tài liệu Markdown của dự án**, "
            "gợi ý câu hỏi học tập liên quan và giúp cậu tìm Mentor bằng trang Tìm Mentor. "
            "Bản cloud hiện **offline**, không có LLM để trả lời tự do ngoài tài liệu. "
            + _EXAMPLES
        )
    return None
