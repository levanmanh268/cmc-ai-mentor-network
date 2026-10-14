import streamlit as st

from llm_client import build_llm_client, llm_enabled
from matching_engine import get_top_matches, generate_match_explanation
from rag_engine import KnowledgeBase, answer_with_rag
from mentors_data import get_mentor_repository
from ui_helpers import (
    STUDENT_YEARS,
    clear_matching,
    mode_label,
    normalize_sources,
    validate_profile,
)

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
        st.success("LLM: configured (API connection not yet verified)")
    else:
        st.info("LLM: offline grounded mode")


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
        st.metric("LLM", "Online" if client else "Offline")

    st.subheader("Luồng sử dụng")
    st.markdown(
        "1. Điền **Hồ sơ cá nhân**.\n"
        "2. Hỏi **AI Assistant** về nội dung trong kho tài liệu.\n"
        "3. Mở **Tìm Mentor** để nhận danh sách phù hợp.\n"
        "4. Mỗi câu trả lời RAG đều hiển thị nguồn đã dùng."
    )

elif page == "👤 Hồ sơ cá nhân":
    st.title("👤 Hồ sơ cá nhân")
    profile = st.session_state.user_profile
    st.info("Hồ sơ chỉ được lưu trong phiên Streamlit hiện tại; không có tài khoản hoặc cơ sở dữ liệu lưu dài hạn.")

    name = st.text_input("Họ và tên", value=profile.get("name", ""))
    years = list(STUDENT_YEARS)
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
        validated, errors = validate_profile(
            name=name, year=year, field_interest=field_interest, goals=goals, bio=bio
        )
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.session_state.user_profile = validated
            clear_matching(st.session_state)
            st.success("Đã lưu hồ sơ trong phiên hiện tại.")
    if st.button("🗑️ Đặt lại hồ sơ phiên"):
        st.session_state.user_profile = {}
        clear_matching(st.session_state)
        st.success("Đã xóa hồ sơ trong phiên. Mentor yêu thích được giữ nguyên.")
        st.rerun()

elif page == "💬 AI Assistant":
    st.title("💬 Grounded AI Assistant")
    st.caption(
        "RAG theo tài liệu Markdown. Nếu không đủ bằng chứng, hệ thống sẽ từ chối suy diễn thay vì bịa."
    )

    if knowledge_base.document_count == 0:
        st.warning(
            "Chưa có tài liệu trong knowledge_base. Hãy thêm file .md rồi khởi động lại ứng dụng."
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.caption("Xóa lịch sử chỉ áp dụng cho phiên này; hồ sơ và mentor yêu thích được giữ nguyên.")
    if st.button("🗑️ Xóa lịch sử hội thoại"):
        st.session_state.messages = []
        st.success("Đã xóa lịch sử hội thoại trong phiên.")

    for message in st.session_state.messages:
        with st.chat_message(message.get("role", "assistant")):
            st.markdown(message.get("content", ""))
            sources = normalize_sources(message.get("sources"))
            if sources:
                with st.expander("Nguồn truy xuất"):
                    for source in sources:
                        st.markdown(f"**{source['name']}** • relevance={source['score']:.3f}")
                        if source["excerpt"]:
                            st.caption(source["excerpt"])
            if message.get("mode"):
                st.caption(mode_label(message["mode"]))

    if prompt := st.chat_input("Ví dụ: Quy trình xử lý một issue GitHub là gì?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Đang truy xuất tài liệu và kiểm tra bằng chứng..."):
                result = answer_with_rag(prompt, knowledge_base, client=client)
            st.markdown(result.answer)

            source_payload = normalize_sources(result.sources)
            if source_payload:
                with st.expander("Nguồn truy xuất", expanded=True):
                    for source in source_payload:
                        st.markdown(f"**{source['name']}** • relevance={source['score']:.3f}")
                        if source["excerpt"]:
                            st.caption(source["excerpt"])
            st.caption(mode_label(result.mode))
            st.caption(f"Độ liên quan cao nhất: {result.top_score:.3f}. Nguồn truy xuất không chứng minh mọi khẳng định là đúng.")

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

    mentor_pool = get_mentor_repository().list()
    fields = sorted({mentor["field"] for mentor in mentor_pool})
    support_types = sorted({value for mentor in mentor_pool for value in mentor["available_for"]})
    field_filter = st.selectbox("Lọc theo lĩnh vực", ["Tất cả", *fields])
    support_filter = st.selectbox("Lọc theo loại hỗ trợ", ["Tất cả", *support_types])
    active_filters = (field_filter, support_filter)
    if st.session_state.get("active_mentor_filters") != active_filters:
        clear_matching(st.session_state)
        st.session_state.active_mentor_filters = active_filters

    if st.button("🔍 Tìm Mentor", type="primary"):
        with st.spinner("Đang xếp hạng mentor..."):
            st.session_state.top_matches = get_top_matches(
                student_profile,
                top_k=3,
                field_filter=None if field_filter == "Tất cả" else field_filter,
                support_filter=None if support_filter == "Tất cả" else support_filter,
            )
            st.session_state.match_explanations = {}
            if not st.session_state.top_matches:
                st.info("Không tìm thấy mentor phù hợp với bộ lọc đã chọn. Hãy thử đổi điều kiện.")

    # Results are stored independently of the search button state so that
    # clicking a mentor's Save button does not make the results disappear.
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
