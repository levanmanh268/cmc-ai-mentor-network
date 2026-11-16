# Đặc tả yêu cầu phi chức năng (NFR) của CMC AI Mentor Network

**Phiên bản:** 2.0, 12/10/2026. Đồng bộ với [architecture.md](architecture.md), tiếp nối bản nháp NFR do Dương Tuấn Dũng (`@TuanDungir`) đưa lên.

> **Không được nhầm mục tiêu với bằng chứng đã đạt.** Các ngưỡng định lượng bên dưới là **đề xuất nội bộ để giảng viên/khách hàng chấp thuận**, chưa phải SLA hay số liệu hệ thống đã đo. `Đã có kiểm tra cơ bản` cũng không đồng nghĩa toàn bộ NFR đạt.

## Phạm vi thử nghiệm và định nghĩa trạng thái

- **Prototype thực tế:** app Streamlit chạy local, lưu hồ sơ và mentor yêu thích trong Session State; không có đăng nhập, persistent DB hoặc tính năng liên hệ mentor.
- **Môi trường baseline cần ghi:** OS, Python 3.11+, phiên bản thư viện, CPU/RAM, số Markdown docs/chunks, số mentor, mode `offline` hoặc `Groq-online`, số lần chạy.
- **P95:** phân vị 95 của thời gian xử lý từ các lần đo, không phải giá trị trung bình.
- **Đã có kiểm tra cơ bản:** có unit/CI/runtime smoke liên quan, nhưng chưa đủ minh chứng nghiệm thu hoàn chỉnh.
- **Chưa xác minh:** chưa có phép đo/tập bằng chứng hoặc chưa đủ kiểm thử.
- **Chưa đáp ứng:** thiết kế hiện tại thiếu tính năng bắt buộc của NFR nếu coi đó là yêu cầu thật.
- **Đề xuất:** khách hàng cần xác nhận phạm vi/ngưỡng trước khi chuyển thành acceptance criteria ràng buộc.

## Bảng NFR có thể truy vết

| ID | Thuộc tính và yêu cầu | Chỉ tiêu nghiệm thu đề xuất (chưa phê duyệt) | Cách đo, bằng chứng dự kiến | Trạng thái hiện tại |
| --- | --- | --- | --- | --- |
| **NFR-01** | Hiệu năng local | Ở offline mode, với dataset demo, P95 tìm mentor **≤2 giây** và truy xuất RAG **≤2 giây**, tối thiểu 100 lượt/luồng, đo warm/cold riêng | Script benchmark `time.perf_counter()`, CSV môi trường, P50/P95; không gộp network latency Groq | **Chưa xác minh** |
| **NFR-02** | Quản lý secret/bảo mật | 100% secret dùng qua environment/secret store, không tồn tại trong **HEAD tracked files**; quét history để phát hiện key cũ; 0 key thật trong PR mới | CI secret guard, manual security review, evidence key cũ đã revoke | **Đã có kiểm tra cơ bản**, history/revoke chưa xác minh |
| **NFR-03** | Quyền riêng tư dữ liệu người dùng (bao gồm lịch sử General Chat và BYOK key) | Không truyền hồ sơ/chat ra provider nếu chưa thông báo rõ và được user đồng ý; không ghi PII vào GitHub logs; quy định retention trước khi có persistence | Review luồng `app.py → client → Groq`, manual consent/UAT, log redaction check | **Đã có cơ chế consent trong UI** (mặc định offline, opt-in trước khi gửi qua Groq); cần bổ sung network/log audit và UAT về việc hiểu đồng ý trước khi kết luận đạt |
| **NFR-04** | Độ bền vững của dữ liệu | **Nếu** yêu cầu dữ liệu còn sau restart: hồ sơ/favorites được khôi phục chính xác qua 10 chu kỳ restart với DB/backup; bản prototype phải hiển thị cảnh báo chỉ giữ trong phiên | Restart persistence test + DB integrity report sau khi triển khai; kiểm thử rõ session life cycle | **Chưa đáp ứng persistence**, do chỉ có `st.session_state`; cần customer approval nếu bổ sung |
| **NFR-05** | Tương thích | Python 3.11 trên **Windows & Linux**, dependency install, pytest và Streamlit health đều thành công với môi trường sạch | GitHub Actions hai OS + log chạy tại máy người dùng | **Đã có CI kiểm tra cơ bản**, không bảo đảm mọi thiết bị |
| **NFR-06** | Usability | Ít nhất 5 người thử, **≥4/5** hoàn thành flow xem dashboard, hỏi RAG, tìm/lưu mentor với hướng dẫn; ghi lỗi từng flow | Kịch bản UAT, thời lượng, observation, bảng đánh giá | **Chưa xác minh** |
| **NFR-07** | Maintainability | Mọi thay đổi tính năng qua Issue/PR; compile + pytest xanh; module domain không tự khởi tạo Groq; không có file trùng tên khi `casefold` | GitHub history, architectural regression checks, static dependency check | **Có nền tảng**, chưa đủ để kết luận toàn diện |
| **NFR-08** | Xử lý lỗi/khả dụng | 100% test case thiếu key, API exception, knowledge base rỗng, query không liên quan và dữ liệu mentor invalid không gây crash không kiểm soát | Unit/AppTest/E2E với fault injection, ghi expected/actual | **Đã có kiểm tra cơ bản**, chưa bao phủ mọi lỗi |
| **NFR-09** | Chất lượng/gắn nguồn của AI | Trên bộ câu hỏi gold tối thiểu 30 câu, tỉ lệ trích dẫn đúng nguồn và từ chối đúng câu ngoài tập ≥ **90%**, báo riêng groundedness/recall (đề xuất) | Đánh giá thủ công có rubric, dataset version, false positives/negatives, independent reviewers | **Chưa xác minh**; hiện có validation ID citation trong `rag_engine.py`, nhưng không chứng minh entailment hay chống hallucination theo nghĩa ngữ nghĩa |
| **NFR-10** | Testability & traceability | Mỗi FR/NFR có ít nhất một test case hoặc UAT cụ thể, PR chỉ merge khi CI xanh, mọi test fail phải ghi rõ reproduction & result | Traceability matrix, CI URL, pytest report, UAT sign-off | **Có CI cơ bản**, coverage tổng thể chưa xác minh |

## Ma trận truy vết chức năng (đúng code)

| Chức năng thực tế | Source-of-truth | NFR liên quan | Kiểm tra đã có / còn cần |
| --- | --- | --- | --- |
| Dashboard | `app.py` | 05, 06, 08 | Streamlit startup/UI smoke; cần UAT |
| Session profile | `app.py` | 03, 04, 06 | AppTest một phần; chưa có DB, cần consent/persistence decision |
| RAG retrieval + fallback | `rag_engine.py` | 01, 08, 09 | `tests/test_rag_engine.py`; cần benchmark và groundedness |
| Mentor matching + repository | `matching_engine.py`, `mentors_data.py` | 01, 07, 08, 09 | `tests/test_matching_engine.py`; cần đánh giá fairness/ranking |
| Optional Groq client + multi-turn chat | `llm_client.py`, `general_chat.py` | 02, 03, 08 | `tests/test_llm_client.py`; chưa kiểm thử với secret thật, cần consent |
| GitHub development workflow | `.github/`, `tests/` | 05, 07, 10 | Linux/Windows Actions; không thay UAT |

## Template ghi bằng chứng cho từng case

| Trường | Yêu cầu điền |
| --- | --- |
| Test ID / NFR | Ví dụ `TC-NFR-01-A` |
| Phiên bản và commit SHA | Hash code chính xác |
| Môi trường | OS, CPU, RAM, Python, packages, nguồn dữ liệu, chế độ Groq |
| Input/workload | Dataset, câu hỏi, số lần thử, concurrency |
| Mục tiêu | Threshold đề xuất đã được thầy/customer chốt |
| Actual | Raw results, P50/P95 nếu đo thời gian, ảnh/log |
| Verdict | Pass/Fail/Not Run; không suy đoán |
| Người kiểm và ngày | Họ tên + thời điểm kiểm |

## Các quyết định cần thầy / khách hàng xác nhận

1. NFR-04: dữ liệu có cần tồn tại sau refresh/restart hay chấp nhận session-only prototype?
2. NFR-03: có cho phép gửi câu hỏi, hồ sơ và dữ liệu mentor lên Groq không? Cần cơ chế consent/minimization nào?
3. NFR-01 và NFR-09: ngưỡng P95 và 90% chỉ là đề xuất; cần thống nhất tập dữ liệu, phương pháp đo, phần cứng.
4. NFR-06: mẫu UAT, tiêu chí chấp nhận, trình duyệt mục tiêu.
5. NFR-02: xác nhận đã revoke key cũ từng bị commit lên GitHub history.

**Nguyên tắc:** không kết luận “đạt tuyệt đối” dựa vào CI xanh; CI chứng minh chỉ các checks đã khai báo được chạy và qua.
