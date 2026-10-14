import streamlit as st

from llm_client import build_llm_client, llm_enabled
from matching_engine import get_top_matches, generate_match_explanation
from rag_engine import KnowledgeBase, answer_with_rag
from ui_helpers import normalize_saved_source, rag_mode_label, source_history_payload

st.set_page_config(page_title="CMC AI Mentor Network", page_icon="🤖", layout="wide")

client = build_llm_client()


@st.cache_resource
def load_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase("knowledge_base")


knowledge_base = load_knowledge_base()


with st.sidebar:
    st.title("🤖 CMC AI Mentor Network")
    st.caption("AI learning support • CMCU course project")
    st.divider()
    page = st.radio(
        "Chọn trang",
        ["🏠 Dashboard", "👤 Hồ sơ cá nhân", "💬 AI Assistant", "👥 Tìm Mentor"],
    )
    st.divider()
    st.caption(
        f"Knowledge base: {knowledge_base.document_count} tài liệu • "
        f"{knowledge_base.chunk_count} chunks"
    )
    if llm_enabled():
        st.info("LLM: đã cấu hình; kết nối và nội dung từng câu trả lời chưa được xác minh đầy đủ.")
    else:
        st.info("LLM: chế độ ngoại tuyến")


if "favorite_mentors" not in st.session_state:
    st.session_state.favorite_mentors = []

if "top_matches" not in st.session_state:
    st.session_state.top_matches = []

if "match_explanations" not in st.session_state:
    st.session_state.match_explanations = {}

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}


if page == "🏠 Dashboard":
    st.title("🏠 CMC AI Mentor Network")
    st.write(
        "Một prototype giáo dục AI gồm trợ lý hỏi đáp có căn cứ theo tài liệu "
        "và hệ thống ghép mentor theo hồ sơ sinh viên."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tài liệu RAG", knowledge_base.document_count)
    with col2:
        st.metric("Chunks đã index", knowledge_base.chunk_count)
    with col3:
        st.metric("LLM", "Đã cấu hình" if client else "Ngoại tuyến")

    st.subheader("Luồng sử dụng")
    st.markdown(
        "1. Điền **Hồ sơ cá nhân**.\n"
        "2. Hỏi **AI Assistant** về nội dung trong kho tài liệu.\n"
        "3. Mở **Tìm Mentor** để nhận danh sách phù hợp.\n"
        "4. Mỗi câu trả lời RAG đều hiển thị nguồn truy xuất và trạng thái."
    )

elif page == "👤 Hồ sơ cá nhân":
    st.title("👤 Hồ sơ cá nhân")
    profile = st.session_state.user_profile

    name = st.text_input("Họ và tên", value=profile.get("name", ""))
    years = ["Năm 1", "Năm 2", "Năm 3", "Năm 4"]
    current_year = profile.get("year", "Năm 1")
    year = st.selectbox(
        "Bạn là sinh viên năm mấy?",
        years,
        index=years.index(current_year) if current_year in years else 0,
    )
    field_interest = st.text_input(
        "Lĩnh vực quan tâm",
        value=profile.get("field_interest", "NLP, LLM, RAG"),
    )
    goals = st.text_input(
        "Mục tiêu",
        value=profile.get("goals", "Làm project AI và chuẩn bị thực tập"),
    )
    bio = st.text_area(
        "Giới thiệu ngắn",
        value=profile.get("bio", "Em muốn cải thiện kỹ năng xây dựng hệ thống AI."),
    )

    if st.button("💾 Lưu hồ sơ", type="primary"):
        st.session_state.user_profile = {
            "name": name.strip(),
            "year": year,
            "field_interest": field_interest.strip(),
            "goals": goals.strip(),
            "bio": bio.strip(),
        }
        st.session_state.top_matches = []
        st.session_state.match_explanations = {}
        st.success("Đã lưu hồ sơ.")
        
elif page == "💬 AI Assistant":
    st.title("💬 AI Assistant")
    st.caption(
        "RAG truy xuất tài liệu Markdown trước khi trả lời. Nguồn truy xuất là bằng chứng tham khảo; "
        "việc xuất hiện trong danh sách nguồn không chứng minh mọi khẳng định đã được xác minh."
    )

    if knowledge_base.document_count == 0:
        st.warning(
            "Chưa có tài liệu trong knowledge_base. Hãy thêm file .md rồi khởi động lại ứng dụng."
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    @st.dialog("Xóa lịch sử hội thoại?")
    def confirm_clear_chat():
        st.write(
            "Thao tác này chỉ xóa tin nhắn trong phiên Streamlit hiện tại. "
            "Hồ sơ cá nhân và danh sách mentor đã lưu sẽ được giữ nguyên."
        )
        confirm = st.checkbox("Tôi hiểu và muốn xóa lịch sử hội thoại", key="confirm_clear_chat")
        if st.button("Xóa lịch sử", type="primary", disabled=not confirm):
            st.session_state.messages = []
            st.rerun()

    clear_col, _ = st.columns([1, 4])
    with clear_col:
        if st.button("🗑️ Xóa lịch sử hội thoại", disabled=not st.session_state.messages):
            confirm_clear_chat()

    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        with st.chat_message(role):
            st.markdown(message.get("content", ""))
            sources = [
                normalized
                for normalized in (
                    normalize_saved_source(item) for item in message.get("sources", [])
                )
                if normalized is not None
            ]
            if sources:
                with st.expander("Nguồn truy xuất"):
                    for source in sources:
                        st.markdown(
                            f"**{source['name']}** • relevance={source['score']:.3f}"
                        )
                        if source["excerpt"]:
                            st.caption(source["excerpt"])
            if role == "assistant" and message.get("mode"):
                st.caption(f"Trạng thái: {rag_mode_label(message.get('mode'))}")

    if prompt := st.chat_input("Ví dụ: Quy trình xử lý một issue GitHub là gì?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Đang truy xuất tài liệu và kiểm tra bằng chứng..."):
                result = answer_with_rag(prompt, knowledge_base, client=client)
            st.markdown(result.answer)

            source_payload = [source_history_payload(item) for item in result.sources]
            if source_payload:
                with st.expander("Nguồn truy xuất", expanded=True):
                    for source in source_payload:
                        st.markdown(
                            f"**{source['name']}** • relevance={source['score']:.3f}"
                        )
                        if source["excerpt"]:
                            st.caption(source["excerpt"])

            st.caption(f"Trạng thái: {rag_mode_label(result.mode)}")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.answer,
                "sources": source_payload,
                "mode": result.mode,
            }
        )

elif page == "👥 Tìm Mentor":
    st.title("👥 Tìm Mentor phù hợp")
    st.caption("Hybrid scoring + giải thích có fallback khi LLM offline")

    student_profile = st.session_state.user_profile or {
        "year": "Năm 1",
        "field_interest": "NLP, LLM, RAG",
        "goals": "Làm project AI",
        "bio": "",
    }

    with st.expander("Hồ sơ dùng để matching"):
        st.json(student_profile)

    if st.button("🔍 Tìm Mentor", type="primary"):
        with st.spinner("Đang xếp hạng mentor..."):
            st.session_state.top_matches = get_top_matches(student_profile, top_k=3)
            st.session_state.match_explanations = {}

    # Keep results independent of the search button rerun state.
    for rank, match in enumerate(st.session_state.top_matches, start=1):
        mentor = match["mentor"]
        mentor_id = mentor["id"]
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"### {rank}. {mentor['name']} • {mentor['title']}")
                st.caption(
                    f"{mentor['company']} • {mentor['field']} • "
                    f"{mentor['experience_years']} năm kinh nghiệm"
                )
                st.write(mentor["bio"])
            with right:
                st.metric("Match", f"{match['hybrid_score']:.1f}%")
                st.caption(f"Semantic: {match['semantic_score']:.1f}%")

            if mentor_id not in st.session_state.match_explanations:
                st.session_state.match_explanations[mentor_id] = generate_match_explanation(
                    student_profile, mentor, match["hybrid_score"], client=client
                )
            st.markdown("**Vì sao phù hợp**")
            st.write(st.session_state.match_explanations[mentor_id])

            saved = any(
                item["id"] == mentor_id for item in st.session_state.favorite_mentors
            )
            if st.button(
                "❤️ Đã lưu" if saved else "❤️ Lưu mentor",
                key=f"save_{mentor_id}",
                disabled=saved,
            ):
                st.session_state.favorite_mentors.append(mentor)
                st.success(f"Đã lưu {mentor['name']}.")

    if st.session_state.favorite_mentors:
        st.divider()
        st.subheader("❤️ Mentor đã lưu")
        for index, mentor in enumerate(st.session_state.favorite_mentors):
            with st.container(border=True):
                st.write(f"**{mentor['name']}** • {mentor['title']} • {mentor['company']}")
                if st.button("Xóa", key=f"delete_{index}"):
                    st.session_state.favorite_mentors.pop(index)
                    st.rerun()

st.divider()
st.caption("CMC AI Mentor Network • Group 6 • Software Engineering")
