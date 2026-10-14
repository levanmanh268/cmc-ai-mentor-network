import streamlit as st

from llm_client import DEFAULT_GROQ_MODEL, build_llm_client, llm_enabled
from general_chat import generate_general_reply
from matching_engine import get_top_matches, generate_match_explanation
from profile_helpers import (
    reset_profile_state,
    safe_student_year,
    save_profile_state,
    validate_profile_fields,
)
from rag_engine import KnowledgeBase, answer_with_rag
from ui_helpers import clear_chat_history, normalize_saved_source, rag_mode_label, source_history_payload

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
    st.subheader("🧠 Kết nối AI thực")
    st.caption(f"Model: `{DEFAULT_GROQ_MODEL}` qua Groq.")
    session_key = st.text_input(
        "Groq API key (chỉ trong phiên này)",
        type="password",
        key="session_groq_api_key",
        help="API key gửi đến máy chủ Render trong kết nối Streamlit của phiên; không đưa vào lịch sử chat, GitHub hay logs.",
        placeholder="Dán API key của cậu tại đây",
    )
    if session_key.strip():
        client = build_llm_client(api_key=session_key)
    if client is not None:
        st.info("Đã có cấu hình kết nối mô hình. Chỉ gửi yêu cầu khi cậu cho phép.")
        online_consent = st.checkbox(
            "Đồng ý gửi câu hỏi, lịch sử chat và ngữ cảnh đến Groq",
            value=False,
            help=(
                "Bắt buộc trước khi gọi AI. Groq sẽ xử lý nội dung gửi đi theo "
                "điều khoản và chính sách riêng; tắt để dừng các yêu cầu mới."
            ),
        )
        st.caption("Tắt đồng ý sẽ ngăn lệnh gọi mới, không thu hồi dữ liệu đã gửi tới nhà cung cấp.")
    else:
        online_consent = False
        st.warning("Chưa kết nối mô hình. Cậu cần Groq API key để trò chuyện với AI thực.")
        st.markdown("[Tạo API key tại Groq Console](https://console.groq.com/keys)")
        st.caption("Nếu quản trị viên cấu hình GROQ_API_KEY trong Render, người dùng vẫn phải đồng ý trước khi gọi API.")

authorized_client = client if online_consent else None


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
        st.metric("LLM", "Cho phép trực tuyến" if authorized_client else "Ngoại tuyến")

    st.subheader("Luồng sử dụng")
    st.markdown(
        "1. Điền **Hồ sơ cá nhân**.\n"
        "2. Hỏi **AI Assistant** về nội dung trong kho tài liệu.\n"
        "3. Mở **Tìm Mentor** để nhận danh sách phù hợp.\n"
        "4. Mỗi câu trả lời RAG đều hiển thị nguồn truy xuất và trạng thái."
    )

elif page == "👤 Hồ sơ cá nhân":
    st.title("👤 Hồ sơ cá nhân")
    st.info(
        "Hồ sơ chỉ được lưu trong phiên Streamlit hiện tại. Ứng dụng chưa có tài khoản "
        "hay cơ sở dữ liệu để lưu bền vững; dữ liệu có thể mất khi phiên kết thúc."
    )
    profile = st.session_state.user_profile
    years = ["Năm 1", "Năm 2", "Năm 3", "Năm 4"]
    current_year = safe_student_year(profile.get("year", "Năm 1"), years)
    form_version = st.session_state.get("profile_form_version", 0)

    name = st.text_input(
        "Họ và tên (không bắt buộc)",
        value=profile.get("name", ""),
        key=f"profile_name_{form_version}",
        max_chars=100,
    )
    year = st.selectbox(
        "Bạn là sinh viên năm mấy?",
        years,
        index=years.index(current_year),
        key=f"profile_year_{form_version}",
    )
    field_interest = st.text_input(
        "Lĩnh vực quan tâm *",
        value=profile.get("field_interest", "NLP, LLM, RAG"),
        key=f"profile_interest_{form_version}",
        max_chars=120,
        help="Bắt buộc, tối đa 120 ký tự.",
    )
    goals = st.text_input(
        "Mục tiêu *",
        value=profile.get("goals", "Làm project AI và chuẩn bị thực tập"),
        key=f"profile_goals_{form_version}",
        max_chars=240,
        help="Bắt buộc, tối đa 240 ký tự.",
    )
    bio = st.text_area(
        "Giới thiệu ngắn (không bắt buộc)",
        value=profile.get("bio", "Em muốn cải thiện kỹ năng xây dựng hệ thống AI."),
        key=f"profile_bio_{form_version}",
        max_chars=500,
        help="Tối đa 500 ký tự.",
    )

    if st.button("💾 Lưu hồ sơ trong phiên", type="primary"):
        cleaned, errors = validate_profile_fields(
            name, year, field_interest, goals, bio, years
        )
        if errors:
            for field in ("name", "field_interest", "goals", "bio"):
                if field in errors:
                    st.error(errors[field])
            st.warning("Hồ sơ chưa được lưu; dữ liệu hồ sơ trước đó vẫn được giữ nguyên.")
        else:
            save_profile_state(st.session_state, cleaned)
            st.success("Đã lưu hồ sơ trong phiên Streamlit hiện tại.")

    @st.dialog("Đặt lại hồ sơ trong phiên?")
    def confirm_reset_profile():
        st.write(
            "Hồ sơ sẽ được xóa khỏi phiên hiện tại và kết quả matching cũ sẽ bị xóa. "
            "Danh sách mentor yêu thích và lịch sử chat không bị xóa."
        )
        confirm_reset = st.checkbox(
            "Tôi xác nhận đặt lại hồ sơ", key="confirm_reset_profile"
        )
        if st.button("Xóa hồ sơ và kết quả matching", type="primary", disabled=not confirm_reset):
            reset_profile_state(st.session_state)
            st.session_state.profile_form_version = form_version + 1
            st.rerun()

    if st.button("Đặt lại / xóa hồ sơ trong phiên"):
        confirm_reset_profile()

elif page == "💬 AI Assistant":
    st.title("🤖 CMC AI Assistant")
    st.caption("Hai chế độ độc lập: hội thoại bằng mô hình ngôn ngữ thực và tra cứu tài liệu có trích nguồn.")
    mode = st.selectbox(
        "Chọn chế độ AI",
        ["🤖 Trò chuyện AI", "📚 Hỏi đáp tài liệu"],
        key="assistant_mode",
        help="Trò chuyện AI không có citation tài liệu. Hỏi đáp tài liệu ưu tiên bằng chứng và có thể từ chối khi thiếu nguồn.",
    )

    if mode == "🤖 Trò chuyện AI":
        st.subheader("Trò chuyện với AI")
        st.caption(
            f"Powered by Groq · {DEFAULT_GROQ_MODEL}. Đây là mô hình ngôn ngữ thực; "
            "không phải chính ChatGPT, Gemini hay Claude. Có thể nhầm lẫn, không có web search trong ứng dụng."
        )
        if authorized_client is None:
            st.warning(
                "🔑 **Chưa bật AI thực.** Nhập Groq API key trong thanh bên "
                "và bật ô đồng ý gửi nội dung đến Groq. "
                "Hệ thống sẽ không giả lập câu trả lời từ một mô hình chưa kết nối."
            )
        else:
            st.success("Đã bật kết nối mô hình ngôn ngữ; có thể hội thoại nhiều lượt trong phiên.")
        if "general_messages" not in st.session_state:
            st.session_state.general_messages = []

        @st.dialog("Xóa lịch sử Trò chuyện AI?")
        def confirm_clear_general_chat():
            st.write("Chỉ xóa hội thoại AI trong phiên này. Hỏi đáp tài liệu, hồ sơ và Mentor yêu thích được giữ nguyên.")
            confirm = st.checkbox("Tôi xác nhận", key="confirm_clear_general")
            if st.button("Xóa hội thoại AI", type="primary", disabled=not confirm):
                st.session_state.general_messages = []
                st.rerun()

        if st.button("🗑️ Xóa cuộc trò chuyện AI", disabled=not st.session_state.general_messages):
            confirm_clear_general_chat()

        for item in st.session_state.general_messages:
            with st.chat_message(item.get("role", "assistant")):
                st.markdown(item.get("content", ""))
                if item.get("role") == "assistant" and item.get("status") == "online":
                    st.caption(f"Phản hồi mô hình · {DEFAULT_GROQ_MODEL} · Chưa được kiểm chứng bằng tài liệu")

        if general_prompt := st.chat_input(
            "Hỏi AI bất kỳ điều gì: code Python, toán, AI, ý tưởng dự án...",
            disabled=authorized_client is None,
            max_chars=3000,
            key="general_ai_prompt",
        ):
            st.session_state.general_messages.append({"role": "user", "content": general_prompt})
            with st.chat_message("user"):
                st.markdown(general_prompt)
            with st.chat_message("assistant"):
                with st.spinner("AI đang suy luận và soạn câu trả lời..."):
                    completion = generate_general_reply(st.session_state.general_messages, client=authorized_client)
                if completion.status == "online":
                    st.markdown(completion.answer)
                    st.caption(f"Phản hồi mô hình · {completion.model} · Không kèm nguồn truy xuất")
                else:
                    st.error(completion.answer)
            st.session_state.general_messages.append({
                "role": "assistant",
                "content": completion.answer,
                "status": completion.status,
            })
    else:
        st.title("💬 Grounded AI Assistant")
        st.caption(
            "RAG truy xuất tài liệu Markdown trước khi trả lời. Nguồn truy xuất là bằng chứng tham khảo; "
            "việc xuất hiện trong danh sách nguồn không chứng minh mọi khẳng định đã được xác minh."
        )
        if authorized_client is None:
            st.info(
                "🧪 **Bản demo offline:** Tớ nhận diện vài lời chào cơ bản; còn với câu hỏi kiến thức, "
                "tớ chỉ truy xuất **3 tài liệu mẫu** và hiển thị nguồn, chưa có LLM để trò chuyện tự do. "
                "Hãy thử: **Quy trình xử lý một Issue GitHub như thế nào?** "
                "hoặc **Làm sao giảm hallucination trong RAG?**"
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
                clear_chat_history(st.session_state)
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
                    result = answer_with_rag(prompt, knowledge_base, client=authorized_client)
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

    from mentors_data import get_mentor_repository

    mentor_pool = get_mentor_repository().list()
    field_choices = ["Tất cả", *sorted({mentor["field"] for mentor in mentor_pool})]
    support_choices = ["Tất cả", *sorted({
        support for mentor in mentor_pool for support in mentor["available_for"]
    })]
    field_filter = st.selectbox("Lọc theo lĩnh vực", field_choices)
    support_filter = st.selectbox("Lọc theo loại hỗ trợ", support_choices)
    active_filters = (field_filter, support_filter)
    if st.session_state.get("active_mentor_filters") != active_filters:
        st.session_state.top_matches = []
        st.session_state.match_explanations = {}
        st.session_state.active_mentor_filters = active_filters

    if st.button("🔍 Tìm Mentor", type="primary"):
        with st.spinner("Đang xếp hạng mentor..."):
            st.session_state.top_matches = get_top_matches(
                student_profile, top_k=3,
                field_filter=None if field_filter == "Tất cả" else field_filter,
                support_filter=None if support_filter == "Tất cả" else support_filter,
            )
            st.session_state.match_explanations = {}
            if not st.session_state.top_matches:
                st.info("Không tìm thấy mentor phù hợp với bộ lọc đã chọn.")

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
                    student_profile, mentor, match["hybrid_score"], client=authorized_client
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
