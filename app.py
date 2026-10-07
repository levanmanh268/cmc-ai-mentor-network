import streamlit as st

from llm_client import build_llm_client, llm_enabled
from matching_engine import get_top_matches, generate_match_explanation
from rag_engine import KnowledgeBase, answer_with_rag

client = build_llm_client()


@st.cache_resource
def load_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase("knowledge_base")


knowledge_base = load_knowledge_base()

st.set_page_config(page_title="CMC AI Mentor Network", page_icon="🤖", layout="wide")

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
        st.success("LLM: online")
    else:
        st.info("LLM: offline grounded mode")


if "favorite_mentors" not in st.session_state:
    st.session_state.favorite_mentors = []

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
        st.success("Đã lưu hồ sơ.")

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

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("Nguồn đã dùng"):
                    for source in message["sources"]:
                        st.caption(
                            f"{source['name']} • relevance={source['score']:.3f}"
                        )

    if prompt := st.chat_input("Ví dụ: Quy trình xử lý một issue GitHub là gì?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Đang truy xuất tài liệu và kiểm tra bằng chứng..."):
                result = answer_with_rag(prompt, knowledge_base, client=client)
            st.markdown(result.answer)

            source_payload = [
                {"name": item.source, "score": item.score}
                for item in result.sources
            ]
            if source_payload:
                with st.expander("Nguồn đã dùng", expanded=True):
                    for item in result.sources:
                        st.markdown(
                            f"**{item.source}** • relevance={item.score:.3f}"
                        )
                        st.caption(item.text[:350] + ("…" if len(item.text) > 350 else ""))

            st.caption(
                f"Mode: {result.mode} • top relevance={result.top_score:.3f}"
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.answer,
                "sources": source_payload,
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
            top_matches = get_top_matches(student_profile, top_k=3)

        for rank, match in enumerate(top_matches, start=1):
            mentor = match["mentor"]
            with st.container(border=True):
                left, right = st.columns([3, 1])
                with left:
                    st.markdown(
                        f"### {rank}. {mentor['name']} • {mentor['title']}"
                    )
                    st.caption(
                        f"{mentor['company']} • {mentor['field']} • "
                        f"{mentor['experience_years']} năm kinh nghiệm"
                    )
                    st.write(mentor["bio"])
                with right:
                    st.metric("Match", f"{match['hybrid_score']:.1f}%")
                    st.caption(f"Semantic: {match['semantic_score']:.1f}%")

                explanation = generate_match_explanation(
                    student_profile,
                    mentor,
                    match["hybrid_score"],
                    client=client,
                )
                st.markdown("**Vì sao phù hợp**")
                st.write(explanation)

                if st.button("❤️ Lưu mentor", key=f"save_{mentor['id']}"):
                    if mentor not in st.session_state.favorite_mentors:
                        st.session_state.favorite_mentors.append(mentor)
                        st.success(f"Đã lưu {mentor['name']}.")
                        st.rerun()

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
