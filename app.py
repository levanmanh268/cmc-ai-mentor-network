import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from matching_engine import get_top_matches, generate_match_explanation

load_dotenv()
_groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
client = Groq(api_key=_groq_api_key) if _groq_api_key else None


@st.cache_resource
def load_rag():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
    )
    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever(search_kwargs={"k": 4})


retriever = load_rag()


def get_ai_response(user_message: str) -> str:
    if client is None:
        return (
            "AI Assistant chưa được cấu hình GROQ_API_KEY. "
            "Hãy copy .env.example thành .env, điền API key riêng của bạn rồi khởi động lại ứng dụng."
        )

    try:
        docs = retriever.invoke(user_message)
        context = "\n\n".join(doc.page_content for doc in docs)

        system_prompt = f"""Bạn là CMC AI Mentor, trợ lý AI dành cho sinh viên Đại học CMC.

Vai trò:
- Hỗ trợ học AI, làm project, debug code, chuẩn bị CV và thực tập.
- Ưu tiên trả lời dựa trên Context được truy xuất.
- Nếu Context chưa đủ, phải nói rõ giới hạn thay vì bịa thông tin.

Nguyên tắc:
- Trả lời ngắn gọn nhưng đầy đủ, bằng tiếng Việt tự nhiên.
- Khi có thể, đưa ví dụ và bước tiếp theo cụ thể.
- Không tiết lộ secret, API key hoặc dữ liệu cấu hình nhạy cảm.

Context:
{context}
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=900,
        )
        return chat_completion.choices[0].message.content
    except Exception:
        return "Xin lỗi, AI đang gặp sự cố kỹ thuật. Bạn vui lòng thử lại sau."


st.set_page_config(page_title="CMC AI Mentor Network", page_icon="🤖", layout="wide")

with st.sidebar:
    st.title("🤖 CMC AI Mentor Network")
    st.caption("Pilot • CMCU AI Students")
    st.divider()
    page = st.radio(
        "Chọn trang",
        ["🏠 Dashboard", "👤 Hồ sơ cá nhân", "💬 AI Assistant", "👥 Tìm Mentor"],
    )
    if not _groq_api_key:
        st.warning("Chưa cấu hình GROQ_API_KEY. Các tính năng LLM sẽ chạy ở chế độ giới hạn.")

if "favorite_mentors" not in st.session_state:
    st.session_state.favorite_mentors = []

if page == "🏠 Dashboard":
    st.title("🏠 Dashboard • CMC AI Mentor Network")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mentor đang có", "5")
    with col2:
        st.metric("Chế độ AI", "Online" if client else "Offline")
    with col3:
        st.metric("Phiên bản", "v1.1")
    st.info("Tạo hồ sơ trước, sau đó dùng AI Matching để tìm mentor phù hợp.")

elif page == "👤 Hồ sơ cá nhân":
    st.title("👤 Hồ sơ cá nhân")
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}

    name = st.text_input(
        "Họ và tên",
        value=st.session_state.user_profile.get("name", "Lê Văn Mạnh"),
    )
    years = ["Năm 1", "Năm 2", "Năm 3", "Năm 4"]
    current_year = st.session_state.user_profile.get("year", "Năm 1")
    year = st.selectbox(
        "Bạn là sinh viên năm mấy?",
        years,
        index=years.index(current_year) if current_year in years else 0,
    )
    field_interest = st.text_input(
        "Lĩnh vực bạn quan tâm",
        value=st.session_state.user_profile.get("field_interest", "NLP, LLM, RAG"),
    )
    goals = st.text_input(
        "Mục tiêu của bạn",
        value=st.session_state.user_profile.get("goals", "Làm project RAG, thực tập AI Engineer"),
    )
    bio = st.text_area(
        "Giới thiệu ngắn về bản thân",
        value=st.session_state.user_profile.get("bio", "Em thích chatbot và hệ thống AI."),
    )

    if st.button("💾 Lưu hồ sơ", type="primary"):
        st.session_state.user_profile = {
            "name": name,
            "year": year,
            "field_interest": field_interest,
            "goals": goals,
            "bio": bio,
        }
        st.success("Đã lưu hồ sơ.")

elif page == "💬 AI Assistant":
    st.title("💬 AI Assistant 24/7")
    st.caption("Hỏi về AI, code, project, CV và thực tập.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hỏi AI Assistant..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Đang xử lý..."):
                response = get_ai_response(prompt)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

elif page == "👥 Tìm Mentor":
    st.title("👥 Tìm Mentor phù hợp")
    st.caption("Hybrid Matching + giải thích tùy chọn bằng LLM")

    if "user_profile" in st.session_state and st.session_state.user_profile:
        with st.expander("Thông tin hồ sơ đang sử dụng"):
            sp = st.session_state.user_profile
            st.write(f"**Năm học:** {sp.get('year')} | **Lĩnh vực:** {sp.get('field_interest')}")

    if st.button("🔍 Tìm Mentor phù hợp", type="primary"):
        student_profile = st.session_state.get(
            "user_profile",
            {
                "year": 1,
                "field_interest": "NLP, LLM, RAG",
                "goals": "Làm project RAG",
                "bio": "",
            },
        )

        with st.spinner("Đang phân tích..."):
            top_matches = get_top_matches(student_profile, top_k=3)
            st.success(f"Tìm được {len(top_matches)} mentor phù hợp.")

            for i, match in enumerate(top_matches, 1):
                mentor = match["mentor"]
                h_score = match["hybrid_score"]
                s_score = match["semantic_score"]

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {i}. {mentor['name']} • {mentor['title']}")
                        st.caption(f"{mentor['company']} • {mentor['experience_years']} năm")
                    with col2:
                        st.metric("Match Score", f"{h_score:.1f}%", delta=f"{s_score:.1f}% semantic")

                    explanation = generate_match_explanation(student_profile, mentor, h_score)
                    st.markdown("**💡 Tại sao phù hợp?**")
                    st.markdown(explanation)

                    if st.button("❤️ Lưu mentor này", key=f"save_{mentor['id']}"):
                        if mentor not in st.session_state.favorite_mentors:
                            st.session_state.favorite_mentors.append(mentor)
                            st.success(f"Đã lưu {mentor['name']}.")
                            st.rerun()

    if st.session_state.favorite_mentors:
        st.divider()
        st.subheader("❤️ Mentor đã lưu")
        for idx, mentor in enumerate(st.session_state.favorite_mentors):
            with st.container(border=True):
                st.markdown(f"**{mentor['name']}** • {mentor['title']}")
                st.caption(f"{mentor['company']} • {mentor['experience_years']} năm kinh nghiệm")
                if st.button("🗑️ Xóa", key=f"delete_{idx}"):
                    st.session_state.favorite_mentors.pop(idx)
                    st.rerun()

st.caption("CMC AI Mentor Network • Course project")
