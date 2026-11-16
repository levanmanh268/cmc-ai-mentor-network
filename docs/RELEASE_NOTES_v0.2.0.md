# CMC AI Mentor Network v0.2.0 | Cloud-integrated Classroom Prototype

> **Nhóm 6, Công nghệ phần mềm, Đại học CMC.** Bản **pre-release** cập nhật sau v0.1.0. Một phiên bản có thể deploy được và chạy CI **không đồng nghĩa 100% không lỗi** hoặc các NFR đã được thầy/khách hàng nghiệm thu.

## 🌐 Truy cập bản demo trên cloud
- **Ứng dụng Streamlit:** https://cmc-ai-mentor-network-group6.onrender.com
- **Kiểm tra trạng thái:** https://cmc-ai-mentor-network-group6.onrender.com/_stcore/health
- **Dịch vụ:** Render web service, Python/Streamlit, region Singapore, gói Free, nguồn `main`.
- **Giới hạn:** Render Free có thể ngủ khi không có truy cập; lần mở đầu có thể chậm. Dữ liệu hồ sơ, chat và mentor yêu thích chỉ lưu trong `st.session_state`, có thể mất khi tải lại/khởi động lại. Không dùng dữ liệu thật nhạy cảm cho demo.
- **AI ngoài:** không yêu cầu `GROQ_API_KEY`; bản cloud được triển khai ở **offline mode**. Trong bản code mới, kể cả cấu hình Groq, người dùng phải chọn đồng ý trước khi câu hỏi/dữ liệu matching được gửi tới dịch vụ ngoài.

## Các tính năng thực sự đã triển khai
1. **AI Assistant**: RAG TF-IDF trên Markdown, hiển thị citations/relevance/excerpts trong chat và lịch sử; trạng thái AI rõ ràng, xử lý mode `online-citations-unverified`, offline fallback và câu hỏi thiếu chứng cứ, có thao tác xóa chat có xác nhận.
2. **Hồ sơ sinh viên**: kiểm tra dữ liệu bắt buộc, giới hạn độ dài, giữ hồ sơ cũ khi nhập sai và đặt lại trong phiên có xác nhận; không có tài khoản hoặc database.
3. **Mentor Matching**: hybrid scoring 65% TF-IDF, 25% domain, 10% experience, có bộ lọc lĩnh vực và loại hỗ trợ, case không kết quả, lưu/xóa favorites trong phiên.
4. **Chẩn đoán dữ liệu mentor CLI**: báo trùng ID, dữ liệu thiếu/sai, unit tests. Phần đóng góp gốc của **Dương Tuấn Dũng, PR #28**, được bảo tồn trong lịch sử commit; không phải tính năng nhập dữ liệu từ màn hình web.
5. **RAG guardrails**: xác thực ID citation thuộc ngữ cảnh, kiểm tra độ phủ từ vựng để giảm false positive của truy vấn ngoài chủ đề và 14-case offline smoke benchmark. **Đây không phải chứng nhận đúng ngữ nghĩa/hallucination thấp như NotebookLM**.
6. **Chất lượng tài liệu**: kiến trúc C4 + 5 Mermaid diagrams render qua CLI v10/v11, NFR, README, test plan, privacy dataflow, checklist UAT, GitHub CI Windows/Linux.

## Truy vết trách nhiệm, Issues và PR
- **PRs đã merge:** [#55](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/55) (Hà Văn Dương, chat), [#56](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/56) (Hà Văn Dương, profile), [#57](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/57) (integration và phần việc các Issues còn lại).
- Các Issues về features được xử lý trong bản này: [#17](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/17), [#18](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/18), [#19](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/19), [#21](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/21), [#23](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/23), [#50](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/50), [#51](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/51).
- Issues [#22 UAT](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/22), [#27 Performance](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/27), [#30-#39 NFR](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/39) yêu cầu bằng chứng riêng; **không suy ra đạt chỉ từ việc release/deploy**, và Issues nào chưa được nghiệm thu thì vẫn phải theo dõi.
- Release [v0.1.0](https://github.com/levanmanh268/cmc-ai-mentor-network/releases/tag/v0.1.0) vẫn giữ nguyên, không thay tag cũ.

## Cách chạy local
Windows: tải Source code ZIP, chạy `run_windows.bat`. Khác: Python 3.11+, cài `pip install -r requirements.txt` rồi chạy `python -m streamlit run app.py`. Không cần Groq key.

Chạy regression và benchmark:
```bash
python -m pytest -q
python mentor_data_diagnostics.py
python -m scripts.evaluate_rag
```

## Bằng chứng sau phát hành
Workflow chỉ tạo tag `v0.2.0` từ commit `main` qua **CI Linux/Windows/Mermaid PASS** và health check HTTP của URL cloud. Ghi chú khi publish được bổ sung link CI của đúng commit và kết quả kiểm tra cloud. Xem thêm [kiến trúc](https://github.com/levanmanh268/cmc-ai-mentor-network/blob/main/docs/architecture.md), [NFR](https://github.com/levanmanh268/cmc-ai-mentor-network/blob/main/docs/non-functional-requirements.md), [Test Plan](https://github.com/levanmanh268/cmc-ai-mentor-network/blob/main/docs/TEST_PLAN.md).
