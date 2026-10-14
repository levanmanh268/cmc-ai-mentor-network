# CMC AI Mentor Network v0.1.0 | Classroom Prototype

> **Bản phát hành đầu tiên của Nhóm 6, môn Công nghệ phần mềm, Đại học CMC.** Đây là bản **prototype để học tập/trình diễn**, KHÔNG phải SaaS hay hệ thống production; không cam kết 0 lỗi, SLA, bảo mật doanh nghiệp hoặc kết quả AI luôn chính xác.

## Chức năng thực sự có trong ứng dụng môn học (root Streamlit)

- **Dashboard:** hiển thị số tài liệu/chunk và trạng thái cấu hình LLM.
- **Hồ sơ sinh viên:** nhập và lưu hồ sơ trong **Streamlit Session State**, không có tài khoản, đăng nhập hay database lưu bền vững.
- **Hỏi đáp có căn cứ:** truy xuất Markdown trong `knowledge_base/` bằng TF-IDF cosine, hiển thị danh sách đoạn nguồn và relevance score. Khi thiếu bằng chứng, trả lời theo chế độ từ chối. Hỗ trợ offline, tùy chọn Groq API nếu người chạy cung cấp key.
- **Ràng buộc citation:** API response phải có citation ID thuộc danh sách đoạn truy xuất; chế độ online `online-citations-unverified` **không chứng nhận mọi claim có căn cứ ngữ nghĩa**.
- **Gợi ý mentor:** hybrid ranking theo TF-IDF (65%), keyword domain overlap (25%), experience fit (10%), với dữ liệu mentor demo trong RAM; giải thích matching có offline fallback; lưu/xóa danh sách mentor yêu thích trong phiên.
- **Tài liệu và kiểm thử:** README, NFR, kiến trúc modular monolith, CI Python trên Windows/Linux, Streamlit HTTP smoke, kiểm tra Mermaid v10/v11 bằng SVG renderer và kiểm tra pattern secret cơ bản.

## Các GitHub Issues đã hoàn thành trước bản phát hành

Các mục dưới đây đã ở trạng thái **Closed** khi chuẩn bị release, có thay đổi đã merge vào `main`:

| Nhóm | Issues |
| --- | --- |
| Bảo mật cấu hình, RAG, matching | [#1](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/1), [#2](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/2), [#3](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/3) |
| CI, tài liệu, hướng dẫn sử dụng | [#4](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/4), [#5](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/5), [#11](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/11), [#13](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/13), [#14](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/14) |
| Data architecture và Windows UX | [#20](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/20), [#24](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/24) |
| Kiến trúc và Mermaid | [#29](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/29), [#40](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/40) |

**Pull Requests minh chứng tiêu biểu (đã merge):** [#6](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/6), [#7](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/7), [#8](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/8), [#9](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/9), [#15](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/15), [#16](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/16), [#26](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/26), [#31](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/31), [#41](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/41) và [#49](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/49).

## Chưa hoàn thành (không được tính là chức năng release)

- Chưa hoàn thành: [#17 benchmark RAG](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/17), [#18 lọc mentor](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/18), [#19 mở rộng QA](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/19), [#21 citation validation workflow của thành viên](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/21), [#22 UAT](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/22), [#23 chẩn đoán data mentor](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/23), [#50 giao diện AI Assistant](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/50), [#51 UI hồ sơ](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/51).
- Bộ NFR [#27](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/27) và [#30 đến #39](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/39) cũng còn phần nghiệm thu/bằng chứng. **CI xanh không đồng nghĩa mọi NFR đã đạt.**
- PR [#28](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/28) của Dương Tuấn Dũng chưa merge tại thời điểm soạn ghi chú, nên chẩn đoán mentor của PR đó **không nằm trong sản phẩm đã phát hành**.
- Không có đăng nhập, đặt lịch/nhắn tin mentor, web search, tải tài liệu qua UI, account database, hoặc chứng minh tính chính xác của LLM ở mức claim.

## Các thư mục portfolio độc lập cùng repository

`cagent_lab/`, `enterprise_doc_ai/`, `retail_ops_ai/`, `edu_trainer_ai/`, `model_pretraining_lab/` và `model_posttraining_lab/` là những **lab chạy riêng**, không phải các microservice được tích hợp vào Streamlit app môn học. Chúng có README, kiểm thử và giới hạn riêng; không nhầm vào tính năng của bản prototype.

## Chạy và kiểm chứng

**Windows:** giải nén Source code (.zip) từ Release, chạy `run_windows.bat`. Có thể chạy offline không cần API key.

**Linux/macOS (Python 3.11+):**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

Mở `http://localhost:8501`. Nếu cần Groq, tạo `.env` **cục bộ** theo `.env.example` và tự cung cấp key riêng, không commit lên Git.

**Tài liệu:** [README](https://github.com/levanmanh268/cmc-ai-mentor-network/blob/main/README.md), [Kiến trúc](https://github.com/levanmanh268/cmc-ai-mentor-network/blob/main/docs/architecture.md), [NFR](https://github.com/levanmanh268/cmc-ai-mentor-network/blob/main/docs/non-functional-requirements.md).

**Bằng chứng CI:** link đến GitHub Actions run trên chính commit phát hành được hệ thống tự chèn khi publish. Mã source trong Release là snapshot của commit đã CI PASS.
