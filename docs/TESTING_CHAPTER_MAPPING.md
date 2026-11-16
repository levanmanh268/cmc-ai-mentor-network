# Đối chiếu nội dung Testing với thực hành của dự án

**Issue:** [#159 — TASK-78: Đối chiếu kết quả với các nội dung trong chương Testing](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/159)  
**Phạm vi:** ứng dụng CMC AI Mentor Network ở thư mục gốc; các lab độc lập chỉ được nhắc đến khi cần phân biệt phạm vi.  
**Ngày rà soát:** 04/11/2026

## Cơ sở và giới hạn

Issue không nêu tên sách, tác giả, ấn bản hoặc số trang của “chương Testing”. Vì vậy, bảng dưới đây đối chiếu với các khái niệm kiểm thử phần mềm phổ biến, không khẳng định là tóm tắt hay trích dẫn chính xác từ một giáo trình cụ thể. Khi được cung cấp tài liệu môn học, cần bổ sung thuật ngữ, trang và điều chỉnh cách diễn giải theo đúng chương.

Các đường dẫn trong cột bằng chứng trỏ tới mã nguồn/tài liệu có thể kiểm tra trong repository. Chúng chứng minh thiết kế và cách chạy kiểm thử; trạng thái PASS chỉ được kết luận từ lần chạy cụ thể gắn với SHA. Không suy diễn rằng mọi kiểm thử đã chạy chỉ vì test case hoặc workflow tồn tại.

## Bảng đối chiếu

| Khái niệm kiểm thử | Thực hành/bằng chứng trong dự án | Đánh giá và khoảng trống |
| --- | --- | --- |
| Lập kế hoạch, phạm vi và tiêu chí thoát | [TEST_PLAN.md](TEST_PLAN.md) mô tả phạm vi và chiến lược; [TESTING_HANDOFF.md](TESTING_HANDOFF.md) định nghĩa cách chạy, phân loại trạng thái và ma trận truy vết. Workflow CI được cấu hình tại [ci.yml](../.github/workflows/ci.yml). | **Đạt một phần.** Có kế hoạch và cổng kiểm tra tự động. Tiêu chí nghiệm thu cho bản phát hành cần gắn với SHA/run cụ thể; CI xanh không thay thế UAT. |
| Mức kiểm thử: đơn vị, tích hợp, hệ thống | Các test trong [tests/](../tests/) kiểm tra helper, matching, RAG, client và UI; nhiều tích hợp dùng provider giả lập. [AppTest flows](../tests/test_end_to_end_flows.py) chạy luồng UI trong tiến trình. [browser_spec.py](../e2e/browser_spec.py) kiểm tra ứng dụng Streamlit thật trên localhost bằng Chromium. | **Có bằng chứng tự động ở nhiều mức**, nhưng AppTest không phải kiểm thử trình duyệt. Chromium localhost cũng không chứng minh ứng dụng public/cloud hoạt động. |
| Thiết kế kiểm thử hộp đen: lớp tương đương và giá trị biên | [test_quality_gates.py](../tests/test_quality_gates.py), [test_profile_helpers.py](../tests/test_profile_helpers.py), [test_matching_engine.py](../tests/test_matching_engine.py) bao phủ đầu vào hợp lệ/không hợp lệ, giá trị rỗng, giới hạn độ dài, top-k và các trường hợp lỗi. | **Đạt một phần.** Có kiểm tra biên và phân lớp đầu vào ở các luồng trọng yếu; chưa có bảng phân hoạch chính thức cho mọi yêu cầu. |
| Kiểm thử nhánh quyết định và luồng trạng thái | Các test về consent/provider, fallback offline, hồ sơ, favorites và chế độ RAG kiểm tra một số nhánh hành vi; xem [test_real_ai_chat.py](../tests/test_real_ai_chat.py), [test_end_to_end_flows.py](../tests/test_end_to_end_flows.py) và [test_streamlit_ui.py](../tests/test_streamlit_ui.py). | **Đạt một phần.** Có test cho các nhánh quan trọng; chưa chứng minh bao phủ đầy đủ mọi tổ hợp điều kiện hay state transition. |
| Kiểm thử âm tính, lỗi và độ bền | [test_llm_client.py](../tests/test_llm_client.py), [test_rag_engine.py](../tests/test_rag_engine.py) kiểm tra lỗi provider, dữ liệu thiếu/không hợp lệ và hành vi từ chối khi thiếu bằng chứng. | **Có kiểm thử tự động được thiết kế.** Mức độ đạt của từng case phải lấy từ JUnit/run đúng SHA; fake provider không xác nhận dịch vụ bên ngoài. |
| Kiểm thử hồi quy và tự động hóa | [ci.yml](../.github/workflows/ci.yml) cấu hình pytest, kiểm tra compile, đánh giá RAG offline, smoke test Streamlit, Windows và các job kiểm tra tài liệu/trình duyệt. | **Có quy trình CI.** Chỉ các job thực sự hoàn tất thành công trên commit được kiểm tra mới là PASS; workflow không chứng minh UAT hoặc chất lượng ngữ nghĩa. |
| Độ bao phủ và độ đầy đủ kiểm thử | Linux CI tạo JUnit và coverage XML; [scripts/testing_report.py](../scripts/testing_report.py) tạo báo cáo kiểm thử. Cấu hình coverage chọn một số module sản phẩm cụ thể trong workflow. | **Đo có giới hạn.** Line coverage theo phạm vi cấu hình không bằng branch/condition coverage, không chứng minh thiếu lỗi và không đo độ đúng của câu trả lời AI. Cần đọc artifacts của run tương ứng trước khi ghi số liệu. |
| Truy vết yêu cầu → test → kết quả | Bảng 39 mục tiêu tại [TESTING_HANDOFF.md](TESTING_HANDOFF.md) ánh xạ yêu cầu, kết quả mong đợi và test automation. Nguyên tắc evidence gắn với SHA/run cũng được nêu trong [TEST_PLAN.md](TEST_PLAN.md). | **Đạt một phần.** Có ma trận test case; việc ánh xạ đầy đủ mọi yêu cầu sản phẩm và bằng chứng run theo từng SHA vẫn cần duy trì. |
| Kiểm thử chấp nhận và khám phá | [UAT_CHECKLIST.md](UAT_CHECKLIST.md) có 10 kịch bản thao tác thủ công và cột ghi kết quả. | **NOT RUN** cho tới khi người thử thực hiện và ghi người kiểm thử, môi trường, ngày, kết quả thực tế và lỗi. Không được đánh dấu PASS dựa trên test tự động. |
| Kiểm thử tích hợp với AI/provider thật | [FINAL_DEFENSE_GATE.md](FINAL_DEFENSE_GATE.md) và [RAG_EVALUATION.md](RAG_EVALUATION.md) phân biệt smoke/evaluator offline với provider thật và chất lượng semantic. | **NOT VERIFIED** nếu chưa có lần chạy BYOK/provider thật được ghi nhận. Bộ dữ liệu demo và proxy hỗ trợ nội dung không chứng minh faithfulness, chất lượng citation ngữ nghĩa hoặc parity với sản phẩm khác. |
| Kiểm thử phi chức năng và bảo mật | CI có secret-pattern guard, timeout/health checks và test privacy/consent; các giới hạn bảo mật được nêu trong [SECURITY.md](../SECURITY.md). | **Đạt một phần.** Đây là regression/smoke tự động, không phải pentest, red-team prompt injection độc lập, kiểm thử tải hay chứng nhận bảo mật. |
| Ghi nhận kết quả và xử lý sai khác | [TESTING_HANDOFF.md](TESTING_HANDOFF.md) quy định PASS/FAIL/SKIPPED/BLOCKED/NOT RUN và yêu cầu lưu JUnit/coverage theo run. | **Đạt ở cấp quy trình.** Kết quả phải bổ sung theo lần chạy cụ thể; test chưa chạy, artifact thiếu hoặc không truy được SHA phải giữ trạng thái chưa xác minh. |

## Kết luận nghiệm thu

- Dự án áp dụng được nhiều nguyên lý kiểm thử phổ biến: lập kế hoạch, kiểm thử nhiều mức, kiểm tra biên/lỗi, hồi quy tự động và truy vết test.
- **Kết quả hiện tại: ĐẠT MỘT PHẦN.** Có bằng chứng về cấu trúc test và CI; mức PASS của phiên bản cần nghiệm thu phải được xác nhận bằng CI/artifacts của đúng commit.
- **Chưa được chứng minh:** UAT người dùng, provider/model thật, độ chính xác ngữ nghĩa của câu trả lời/citation, kiểm thử tải, pentest và độ bao phủ đầy đủ mọi yêu cầu.
- Không có thông tin sách/chương/ấn bản/trang trong issue, nên phần đối chiếu theo giáo trình cụ thể là **BLOCKED** cho đến khi nhóm cung cấp tài liệu được giao.

## Bằng chứng kiểm tra tại thời điểm rà soát

| Hạng mục | Kết quả | Giới hạn |
| --- | --- | --- |
| `main` tại SHA `33819ff51575596c5c17bb2ec79c8a43b0e985c7` | [CI run #41601450058](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/41601450058) hoàn tất với conclusion `success`. | Run có trước các thay đổi tài liệu này; không phải bằng chứng CI cho nội dung mới. |
| Artifacts của run trên | Có `testing-evidence-linux`, `testing-evidence-windows` và `testing-evidence-chromium`. | Tóm tắt run/artifact đã kiểm tra không cung cấp số PASS/FAIL/SKIP hoặc coverage; không tự suy ra số liệu. |
| Pytest tài liệu trong workspace hiện tại | **BLOCKED**: `py -3` không khởi chạy được vì interpreter cấu hình tại `E:\python3.14t.exe` không tồn tại. | Đây là môi trường không chạy được test, không phải kết quả test FAIL. |
| SHA cho các thay đổi tài liệu hiện tại | **NOT VERIFIED**: workspace này không có metadata Git để xác định commit. | Cần chạy CI sau khi các thay đổi được đưa vào branch/commit. |

## Quy trình cập nhật khi có tài liệu môn học

1. Ghi tên sách, tác giả, ấn bản và chương/trang được giao.
2. Thay các khái niệm tổng quát bằng thuật ngữ đúng trong tài liệu; thêm số trang, không chép nguyên văn dài.
3. Với từng khái niệm, trỏ đến test/tài liệu và ghi rõ bằng chứng của SHA/run đã kiểm tra.
4. Giữ các hạng mục không thực hiện ở trạng thái BLOCKED, NOT RUN hoặc NOT VERIFIED; không tự chuyển thành PASS.
