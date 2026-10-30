"""Small, dependency-light presentation helpers for the Streamlit UI."""

from __future__ import annotations

from typing import Any, MutableMapping


RAG_MODE_LABELS = {
    "local-social": "Phản hồi chào hỏi cục bộ (không truy xuất tài liệu và không gọi mô hình AI).",
    "no-evidence": "Chưa tìm thấy bằng chứng phù hợp",
    "offline-grounded": "Trả lời ngoại tuyến dựa trên tài liệu truy xuất",
    "online-citations-unverified": (
        "Có dùng mô hình trực tuyến; mã nguồn trích dẫn đã được kiểm tra, "
        "nhưng nội dung chưa được xác minh ngữ nghĩa"
    ),
    "offline-fallback": (
        "Đã dùng câu trả lời dự phòng ngoại tuyến sau khi phản hồi trực tuyến "
        "không vượt qua kiểm tra trích dẫn"
    ),
}


def rag_mode_label(mode: str | None) -> str:
    """Return a truthful Vietnamese label for a known or legacy RAG mode."""
    if not mode:
        return "Không có thông tin trạng thái RAG"
    return RAG_MODE_LABELS.get(mode, f"Trạng thái RAG chưa được nhận diện ({mode})")


def source_history_payload(source: Any) -> dict[str, Any]:
    """Normalize a retrieved chunk or an older saved source into safe history data."""
    if isinstance(source, dict):
        name = source.get("name") or source.get("source") or "Nguồn không xác định"
        score = source.get("score", 0.0)
        excerpt = source.get("excerpt") or source.get("text") or ""
    else:
        name = getattr(source, "source", None) or "Nguồn không xác định"
        score = getattr(source, "score", 0.0)
        excerpt = getattr(source, "text", "") or ""

    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0

    excerpt = str(excerpt).strip()
    return {
        "name": str(name),
        "score": max(0.0, min(1.0, score)),
        "excerpt": excerpt[:350] + ("…" if len(excerpt) > 350 else ""),
    }


def normalize_saved_source(source: Any) -> dict[str, Any] | None:
    """Normalize legacy history entries without crashing on missing fields."""
    if not isinstance(source, dict):
        return None
    return source_history_payload(source)


def clear_chat_history(session_state: MutableMapping[str, Any]) -> None:
    """Clear only the chat message list, preserving profile and favorites."""
    session_state["messages"] = []


def clear_general_chat_history(session_state: MutableMapping[str, Any]) -> None:
    """Clear only the general AI conversation, preserving other session state."""
    session_state["general_messages"] = []
