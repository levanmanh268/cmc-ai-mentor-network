# SEC-10 | Data inventory, use purposes, recipients and privacy notice

**Issue:** #178. **Scope:** Streamlit root app. **Owner proposed:** Nguyễn Văn Phúc. The inventory reflects current code; it does not prove a legal compliance audit.

| Data | Collected? | Purpose | Storage/retention in app | May go to Groq? | User control |
| --- | --- | --- | --- | --- | --- |
| Student name (optional) | User enters | Show personal profile | Session RAM, clears via reset/session end | Not directly in current RAG prompt | Edit/reset |
| Year, field_interest, goals | User enters | Mentor matching; explanations | Session RAM | Optional mentor explanation with consent | Edit/reset |
| Bio (optional) | User enters | Matching context | Session RAM | Not directly in current matching explanation | Edit/reset |
| RAG question and retrieved snippets | User enters/repository | Grounded QA | Session RAM; public KB files | Yes only if consent checked and valid key | Clear RAG history; disable new transmissions |
| General chat messages | User enters/provider output | Conversation context | Session RAM, bounded recent history to API | Yes after consent | Clear general chat; disable consent |
| Favorite demo mentors | User saves | Session convenience | Session RAM only | Not as a favorite list | Remove favorite |
| BYOK Groq API credential | User pastes (optional) | Provider authentication | Browser widget -> server session RAM; SDK transmits to Groq | Auth header to provider | Clear field/close session; revoke at provider |
| Server GROQ_API_KEY | Operator configured | Optional shared-provider access | Server environment | Yes as API auth | Operator rotates |
| App usage/HTTP logs | Hosted infrastructure | Operations/security | Platform-level; not determined by repository alone | No app-defined transfer | Provider policy, UNKNOWN |

**No root database, email/SMS identity system, account registration, durable cloud profile storage or user-facing account deletion endpoint.** Do not claim such features.

## Notice displayed to users (proposed truthful wording)
"Thông tin hồ sơ và lịch sử trò chuyện được lưu tạm trong phiên dùng ứng dụng. Khi bật đồng ý kết nối AI, câu hỏi, lịch sử liên quan và trích đoạn tài liệu có thể được gửi đến Groq để xử lý; đây là nhà cung cấp bên ngoài. Tắt đồng ý chỉ chặn yêu cầu mới, không xóa dữ liệu đã gửi cho bên cung cấp. Nếu tự nhập API key, key được truyền tới máy chủ Streamlit rồi dùng để gọi Groq, không chỉ nằm trên trình duyệt. Không nhập thông tin nhạy cảm không cần thiết."

## Privacy minimization and user testing
- Do not require real full name if matching does not need it; test field can remain optional.
- Avoid private data in sample cases, screenshots, commit messages and public artifacts.
- Test that opt-in false denies provider, clearing profile/chat affects session only and does not claim external deletion.
- Obtain consent/appropriate authorization for human UAT; use fictional names.
- Investigate third-party retention and privacy notices before using real personal data.

See `docs/PRIVACY_DATAFLOW.md`, `docs/privacy/data-controls.md`, #178.
