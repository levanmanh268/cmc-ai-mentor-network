import streamlit as st
from groq import Groq
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from matching_engine import get_top_matches, generate_match_explanation

client = Groq(api_key="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")

@st.cache_resource
def load_rag():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={'device': 'cpu'}
    )
    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )
    return vectorstore.as_retriever(search_kwargs={"k": 4})

retriever = load_rag()


def get_ai_response(user_message: str) -> str:
    try:
        docs = retriever.invoke(user_message)
        context = "\n\n".join([doc.page_content for doc in docs])

        # ==================== PROMPT RAG ĐÃ NÂNG CẤP ====================
        system_prompt = f"""Bạn là **CMC AI Mentor** – trợ lý AI chuyên nghiệp, tận tâm và giàu kinh nghiệm của trường Đại học CMC.

**Vai trò của bạn:**
- Hỗ trợ sinh viên CMCU ngành AI học tập, làm project, debug code, chuẩn bị CV và thực tập.
- Trả lời chính xác, hữu ích dựa trên tài liệu được cung cấp ở phần **Context** bên dưới.
- Nếu Context không có thông tin đầy đủ, hãy trả lời dựa trên kiến thức chung một cách cẩn thận và minh bạch.

**Nguyên tắc trả lời (rất quan trọng):**
- Trả lời **ngắn gọn nhưng đầy đủ**, dễ hiểu.
- Sử dụng tiếng Việt tự nhiên, thân thiện.
- Khi giải thích khái niệm phức tạp, nên đưa ví dụ minh họa nếu có thể.
- Nếu có thể, hãy gợi ý thêm hướng học tập hoặc project liên quan.
- Khuyến khích sinh viên hỏi thêm chi tiết nếu cần.

**Context (Tài liệu liên quan được truy xuất):**
{context}
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=900,
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        return "Xin lỗi, hiện tại AI đang gặp sự cố kỹ thuật. Bạn vui lòng thử lại sau nhé!"


# ==================== GIAO DIỆN ====================
st.set_page_config(page_title="CMC AI Mentor Network", page_icon="🤖", layout="wide")

with st.sidebar:
    st.title("🤖 CMC AI Mentor Network")
    st.caption("Pilot - CMCU AI Students")
    st.divider()
    page = st.radio("Chọn trang", ["🏠 Dashboard", "👤 Hồ sơ cá nhân", "💬 AI Assistant", "👥 Tìm Mentor"])

if "favorite_mentors" not in st.session_state:
    st.session_state.favorite_mentors = []

if page == "🏠 Dashboard":
    st.title("🏠 Dashboard - CMC AI Mentor Network")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Mentor gợi ý", "12")
    with col2: st.metric("Cuộc chat AI", "47")
    with col3: st.metric("Mức độ hài lòng", "4.8/5")
    st.success("✅ Đã match với 3 mentor AI")

elif page == "👤 Hồ sơ cá nhân":
    st.title("👤 Hồ sơ cá nhân")
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}

    name = st.text_input("Họ và tên", value=st.session_state.user_profile.get("name", "Lê Văn Mạnh"))
    year = st.selectbox("Bạn là sinh viên năm mấy?", ["Năm 1", "Năm 2", "Năm 3", "Năm 4"],
                        index=["Năm 1", "Năm 2", "Năm 3", "Năm 4"].index(st.session_state.user_profile.get("year", "Năm 1")))
    field_interest = st.text_input("Lĩnh vực bạn quan tâm", value=st.session_state.user_profile.get("field_interest", "NLP, LLM, RAG"))
    goals = st.text_input("Mục tiêu của bạn", value=st.session_state.user_profile.get("goals", "Làm project RAG, thực tập AI Engineer"))
    bio = st.text_area("Giới thiệu ngắn về bản thân", value=st.session_state.user_profile.get("bio", "Em thích làm chatbot và hệ thống AI thông minh"))

    if st.button("💾 Lưu hồ sơ", type="primary"):
        st.session_state.user_profile = {"name": name, "year": year, "field_interest": field_interest, "goals": goals, "bio": bio}
        st.success("✅ Hồ sơ đã được lưu!")
        st.balloons()

elif page == "💬 AI Assistant":
    st.title("💬 AI Assistant 24/7 - CMC AI Mentor")
    st.caption("Hỏi bất cứ thứ gì về AI, code, project, CV, thực tập...")

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
            with st.spinner("Đang suy nghĩ..."):
                response = get_ai_response(prompt)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

elif page == "👥 Tìm Mentor":
    st.title("👥 Tìm Mentor Phù Hợp")
    st.caption("AI Matching thông minh • Hybrid Scoring + LLM giải thích")

    if "user_profile" in st.session_state and st.session_state.user_profile:
        with st.expander("📋 Thông tin hồ sơ đang sử dụng"):
            sp = st.session_state.user_profile
            st.write(f"**Năm học:** {sp.get('year')} | **Lĩnh vực:** {sp.get('field_interest')}")

    if st.button("🔍 Tìm Mentor Phù Hợp", type="primary"):
        student_profile = st.session_state.get("user_profile", {
            "year": 1, "field_interest": "NLP, LLM, RAG", "goals": "Làm project RAG", "bio": ""
        })

        with st.spinner("Đang phân tích..."):
            top_matches = get_top_matches(student_profile, top_k=3)
            st.success(f"✅ Tìm được {len(top_matches)} mentor phù hợp!")

            for i, match in enumerate(top_matches, 1):
                mentor = match["mentor"]
                h_score = match["hybrid_score"]
                s_score = match["semantic_score"]

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {i}. {mentor['name']} — {mentor['title']}")
                        st.caption(f"{mentor['company']} • {mentor['experience_years']} năm")
                    with col2:
                        st.metric("Match Score", f"{h_score:.1f}%", delta=f"{s_score:.1f}% semantic")

                    explanation = generate_match_explanation(student_profile, mentor, h_score)
                    st.markdown("**💡 Tại sao phù hợp?**")
                    st.markdown(explanation)

                    col_btn1, col_btn2 = st.columns([1, 3])
                    with col_btn1:
                        if st.button("❤️ Lưu mentor này", key=f"save_{mentor['id']}"):
                            if mentor not in st.session_state.favorite_mentors:
                                st.session_state.favorite_mentors.append(mentor)
                                st.success(f"Đã lưu {mentor['name']}")
                                st.rerun()

    if st.session_state.favorite_mentors:
        st.divider()
        st.subheader("❤️ Mentor đã lưu")
        for idx, mentor in enumerate(st.session_state.favorite_mentors):
            with st.container(border=True):
                st.markdown(f"**{mentor['name']}** — {mentor['title']}")
                st.caption(f"{mentor['company']} • {mentor['experience_years']} năm kinh nghiệm")
                if st.button("🗑️ Xóa", key=f"delete_{idx}"):
                    st.session_state.favorite_mentors.pop(idx)
                    st.rerun()

st.caption("Prototype v1 - CMC AI Mentor Network | Built for CMCU Innovation Contest")