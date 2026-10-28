# CMC AI Mentor Network

[![CI](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/workflows/ci.yml/badge.svg)](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🏪 **RetailOps AI Lab:** [synthetic convenience-store operations](retail_ops_ai/README.md) with versioned store-policy retrieval, price and inventory tools, source-linked receipt extraction, FastAPI and CI.
> 🎓 **EduTrainer AI Lab:** [synthetic education AI and trainer evaluation](edu_trainer_ai/README.md) with course RAG, quiz bank, rubric review, allowlisted tools, optional mocked LLM and CI.
> **Both are independently developed portfolio case studies, NOT official 7-Eleven or FUNiX products or employment deliverables.**
> 🔬 **Model training capability labs (independent portfolios; NOT FUNiX deliverables):**
> [Pre-training from scratch](model_pretraining_lab/README.md): split-safe causal bigram language modeling, cross-entropy/SGD, numerical gradient tests.
> [Post-training SFT + DPO](model_posttraining_lab/README.md): response-only supervised fine-tuning, frozen reference, analytical preference-optimization gradients and transparent validation failures.
> Both use fictional datasets, run offline on CPU, and demonstrate training mechanics rather than large-scale LLM capability.
> 🚀 **Featured AI Engineer Portfolio (2026):** [Enterprise Document AI](enterprise_doc_ai/README.md). Independent case study implementing access-scoped enterprise retrieval, document versioning, BM25 and hybrid RRF, invoice field extraction with provenance, review-gated workflows, optional LLM generation, FastAPI, and an **80-question transparent synthetic evaluation**. [Runnable tests and evaluation CI](.github/workflows/enterprise-doc-ai.yml). Not affiliated with the proprietary CMC C-Agent implementation.

> 🔬 **Technical extension (2026):** [C-Agent Capability Lab](cagent_lab/README.md) explores BM25/TF-IDF retrieval, optional semantic embeddings, optional LLM generation, offline evaluation, a guarded tool router and FastAPI. Its small synthetic benchmark is a software-validation demonstration, not an enterprise accuracy claim.

> **NEW independent AI engineering case study:** [Enterprise Document AI](enterprise_doc_ai/README.md) demonstrates permission-scoped RAG, BM25/character hybrid retrieval, document field extraction with provenance, 80 published synthetic QA cases, opt-in citation-checked LLM, approval-gated workflows and Linux/Windows regression CI. [Technical results](enterprise_doc_ai/docs/EVALUATION_REPORT.md). This is **not** CMC proprietary software and does not claim enterprise-level accuracy.

> **Nhóm 6 · Môn Công nghệ phần mềm · CMC University**

**CMC AI Mentor Network** là prototype hỗ trợ học tập AI cho sinh viên, kết hợp một trợ lý hỏi đáp có căn cứ theo tài liệu và hệ thống gợi ý mentor có thể giải thích được. Repository được tổ chức theo quy trình phát triển phần mềm có truy vết: **Issue → Branch → Commit → Pull Request → CI → Review → Merge**.

> Dữ liệu mentor và tài liệu trong repository là dữ liệu demo phục vụ học tập, không phải thông tin hay chính sách chính thức của Đại học CMC.

## Mục lục

- [Bài toán](#bài-toán)
- [Tính năng chính](#tính-năng-chính)
- [Kiến trúc tổng quan](#kiến-trúc-tổng-quan)
- [Cách chạy nhanh](#cách-chạy-nhanh)
- [Cách sử dụng](#cách-sử-dụng)
- [Kiểm thử và chất lượng](#kiểm-thử-và-chất-lượng)
- [Cấu trúc repository](#cấu-trúc-repository)
- [Quy trình làm việc với GitHub Issues](#quy-trình-làm-việc-với-github-issues)
- [AI safety và giảm hallucination](#ai-safety-và-giảm-hallucination)
- [Nhóm phát triển](#nhóm-phát-triển)
- [Security và License](#security-và-license)

## Bài toán

Sinh viên mới học AI thường gặp ba khó khăn:

1. Tài liệu học tập phân tán, khó tìm câu trả lời có căn cứ.
2. Chatbot sinh ngôn ngữ có thể trả lời trôi chảy nhưng thiếu bằng chứng.
3. Khó xác định mentor phù hợp với lĩnh vực, mục tiêu và mức kinh nghiệm hiện tại.

CMC AI Mentor Network giải quyết bài toán này bằng hai luồng độc lập nhưng bổ trợ nhau: **Grounded RAG** cho hỏi đáp tài liệu và **Explainable Mentor Matching** cho gợi ý mentor.

## Tính năng chính

| Tính năng | Mô tả |
| --- | --- |
| Trò chuyện AI thực | GPT-OSS 120B qua Groq, đa lượt, nhớ ngữ cảnh gần đây trong phiên, cần API key + opt-in |
| Grounded AI Assistant | Chế độ riêng: truy xuất tài liệu Markdown bằng TF-IDF + cosine similarity và hiển thị citation |
| Citation | Hiển thị nguồn và relevance score để người dùng kiểm chứng |
| No-evidence refusal | Từ chối suy diễn khi không tìm được bằng chứng đủ liên quan |
| Offline-safe mode | Không có Groq API key vẫn dùng được retrieval và fallback |
| Local small-talk | Nhận diện lời chào/cảm ơn ngắn bằng template cục bộ; không biến thành câu hỏi truy xuất hoặc tự nhận là LLM |
| Mentor Matching | Xếp hạng mentor bằng TF-IDF cosine similarity + domain overlap + experience fit |
| Explainable ranking | Hiển thị match score và lý do phù hợp |
| Mentor filters | Lọc theo lĩnh vực và loại hỗ trợ trước khi xếp hạng |
| Session UX | Validate hồ sơ, xóa chat, đặt lại hồ sơ và hiển thị rõ trạng thái/citations |
| Data quality CLI | Chẩn đoán dữ liệu mentor với báo cáo lỗi deterministic, chạy offline |
| Customer workflow | Có Issue Forms cho customer request và bug report |
| CI quality gate | Secret guard, compile check, pytest và Streamlit runtime health check |

## Kiến trúc tổng quan

```text
                         ┌─────────────────────┐
                         │       Người dùng    │
                         └──────────┬──────────┘
                                    │
                                    v
                         ┌─────────────────────┐
                         │   Streamlit UI      │
                         │      app.py         │
                         └───┬──────┬──────┬──┘
                             │      │      │
                             │      │      └──────────────┐
                             │      │                     v
                             │      │              ┌──────────────┐
                             │      │              │ llm_client.py │
                             │      │              └──────┬───────┘
                             │      │                     │ optional
                             v      v                     v
                    ┌──────────────┐  ┌─────────────────┐  Groq API
                    │ RAG Engine   │  │ Matching Engine │
                    │rag_engine.py │  │matching_engine.py│
                    └──────┬───────┘  └────────┬────────┘
                           │                    │
                           v                    v
                 knowledge_base/*.md      mentors_data.py

          LLM client được app.py tạo một lần rồi inject vào các engine.
```

Thiết kế ưu tiên **khả năng kiểm thử**, **khả năng giải thích**, **maintainability** và **graceful degradation** khi dịch vụ LLM không khả dụng. Tài liệu chuẩn: [Kiến trúc hệ thống, gồm 5 sơ đồ đã kiểm thử render](docs/architecture.md) và [Yêu cầu phi chức năng NFR-01 đến NFR-10](docs/non-functional-requirements.md). Các tài liệu phân biệt rõ chức năng đang có và tính năng đề xuất.

## Các AI lab độc lập cùng repository

Ngoài ứng dụng môn học dùng Streamlit ở thư mục gốc, repository còn chứa các demo/portfolio **độc lập**, có README và CI riêng: [C-Agent Lab](cagent_lab/README.md), [Enterprise Document AI](enterprise_doc_ai/README.md), [RetailOps AI](retail_ops_ai/README.md), [EduTrainer AI](edu_trainer_ai/README.md), [Pre-training Lab](model_pretraining_lab/README.md) và [Post-training Lab](model_posttraining_lab/README.md). Các lab này **không phải microservices hoặc plugin được tích hợp vào CMC AI Mentor Network**. Xem phần 2.1 của [kiến trúc chuẩn](docs/architecture.md) để phân biệt ranh giới và trách nhiệm từng hệ thống.

## Demo cloud trực tuyến

🌐 **Ứng dụng:** https://cmc-ai-mentor-network-group6.onrender.com

- Chạy Streamlit trên Render (Singapore, Free). **Trò chuyện AI** dùng GPT-OSS 120B thực qua Groq sau khi có key và người dùng đồng ý; không cấu hình key thì **chỉ RAG offline và Mentor matching** hoạt động.
- Có thể nhập Groq API key **ngay trong sidebar (ô mật khẩu, chỉ trong phiên)** và bật đồng ý để kích hoạt mô hình mà không cần sửa code. Hoặc quản trị viên đặt `GROQ_API_KEY` dưới Render Environment (các phiên vẫn phải opt-in). **Không nhập khóa thật vào chat hay GitHub**.
- Cloud có thể khởi động chậm do gói Free. Hồ sơ, lịch sử chat và mentor yêu thích **chỉ nằm trong phiên**; không có tài khoản/database.
- Theo dõi [hướng dẫn cloud](docs/CLOUD_DEPLOYMENT.md). [Ghi chú bản tích hợp AI thật v0.3.0](docs/RELEASE_NOTES_v0.3.0.md) mô tả cách nhập Groq API key, giới hạn hiện tại và bằng chứng kiểm thử. Chỉ xem là bản đã phát hành khi GitHub Releases xác nhận tag.
- **Trước buổi bảo vệ:** xem [Final Defense Gate – rủi ro P0/P1, checklist và demo 3 phút](docs/FINAL_DEFENSE_GATE.md). Nút **Kiểm tra AI thật ngay** chỉ xuất hiện sau khi có key và tick đồng ý; CI không thay thế bài test API thật.

## Phiên bản phát hành và chứng cứ Issues

- 📦 **GitHub Releases:** [Xem các bản đã phát hành](https://github.com/levanmanh268/cmc-ai-mentor-network/releases).
- **Bản đầu:** `v0.1.0 | Classroom Prototype`, đã phát hành; phiên bản mới `v0.2.0 | Cloud-integrated Classroom Prototype` chỉ được đánh dấu đã phát hành khi GitHub Releases xác nhận.  [Ghi chú phát hành](docs/RELEASE_NOTES_v0.1.0.md) gồm tính năng thực tế, link các Issues đã đóng, Issues còn mở, hướng dẫn chạy và bằng chứng CI trên commit phát hành.
- **Quy trình phát hành:** [RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md). Chỉ gắn tag sau CI PASS trên `main`; một Issue đang mở hoặc PR chưa merge **không** được tính là tính năng đã phát hành.
- **Theo dõi công việc:** [Closed Issues](https://github.com/levanmanh268/cmc-ai-mentor-network/issues?q=is%3Aissue+is%3Aclosed) | [Open Issues](https://github.com/levanmanh268/cmc-ai-mentor-network/issues?q=is%3Aissue+is%3Aopen) | [Pull Requests](https://github.com/levanmanh268/cmc-ai-mentor-network/pulls).

## Cách chạy nhanh

Yêu cầu: **Python 3.11+**.

### Windows: cách đơn giản nhất (khuyến nghị)

Tải repo về hoặc `git clone`, rồi **nhấp đúp `run_windows.bat`** trong thư mục gốc. Trình khởi chạy tự tạo `.venv`, cài các thư viện và chạy Streamlit. Nếu trình duyệt không tự bật, mở **http://localhost:8501**. Không cần tạo `.env` khi chỉ muốn dùng offline demo.

Nếu chạy lỗi: giữ cửa sổ `run_windows.bat` đang mở, **sao chép toàn bộ nội dung lỗi** (che API key nếu có) và gửi vào GitHub Issue. Xem [Hướng dẫn sửa lỗi Windows](docs/WINDOWS_TROUBLESHOOTING.md).

### Cài đặt thủ công

### 1. Clone repository

```bash
git clone https://github.com/levanmanh268/cmc-ai-mentor-network.git
cd cmc-ai-mentor-network
```

### 2. Tạo virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Cài dependency

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Cấu hình Groq tùy chọn

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Sau đó điền key riêng vào `.env`:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Nếu không cấu hình key, ứng dụng vẫn chạy **RAG offline và Mentor Matching**, nhưng **không sinh hội thoại AI tổng quát**. Có 2 cách kích hoạt:
1. Người dùng mở website, dán API key từ [Groq Console](https://console.groq.com/keys) vào ô mật khẩu ở sidebar; key nằm trong Streamlit Session State tại máy chủ Render và mất khi phiên kết thúc.
2. Quản trị viên đặt biến môi trường `GROQ_API_KEY` ở Render Dashboard để người dùng không phải tự mang key. Nếu public, nên có auth/quota/rate limit trước khi bật cho nhiều người (tránh lạm dụng hoặc phát sinh chi phí).

**Cả hai đều cần người dùng tick đồng ý** gửi câu hỏi/lịch sử/ngữ cảnh đến Groq trong phiên; tắt ô để ngừng gửi yêu cầu mới. Không chia sẻ API key cá nhân vào GitHub, email, hình chụp hoặc hội thoại. Model mặc định `openai/gpt-oss-120b` qua Groq, không phải dịch vụ ChatGPT chính thức. Phí/quota phụ thuộc tài khoản Groq.

### 5. Khởi động

```bash
streamlit run app.py
```

Mặc định Streamlit mở tại `http://localhost:8501`.

## Cách sử dụng

### Hồ sơ cá nhân

Điền năm học, lĩnh vực quan tâm, mục tiêu và giới thiệu ngắn. Hồ sơ này được dùng cho Mentor Matching, **chỉ lưu trong phiên Streamlit**, không có đăng nhập hoặc cơ sở dữ liệu người dùng. Trường lĩnh vực và mục tiêu bắt buộc có nội dung; có nút đặt lại hồ sơ.

### 🤖 Trò chuyện AI (mô hình ngôn ngữ thực)

Mở **AI Assistant → 🤖 Trò chuyện AI** (mặc định). Có thể chào hỏi tự nhiên, học toán, lập trình, viết nội dung, đặt câu hỏi tiếp theo về lời đáp trước. Đây là suy luận và sinh câu trả lời qua `openai/gpt-oss-120b`, **không phải câu trả lời cố định**. Lịch sử `general_messages` có giới hạn và chỉ giữ trong phiên; không hỗ trợ internet search, tải file hoặc trí nhớ bền vững. Nếu chưa có credential/consent thì ô chat **không nhận tin nhắn** để tránh giả lập AI online. Có nút xóa riêng.

### 📚 Hỏi đáp tài liệu (RAG)

Chuyển chế độ từ hộp chọn. Hỏi câu liên quan đến tài liệu trong `knowledge_base/`. Hệ thống:

1. chuẩn hóa câu hỏi;
2. truy xuất top-k chunks với kiểm tra lexical coverage nhằm giảm câu hỏi ngoài miền bị match do từ quá chung;
3. áp dụng relevance threshold;
4. chỉ gửi context đã truy xuất cho LLM;
5. hiển thị nguồn đã dùng.

Nếu retrieval không đủ bằng chứng, hệ thống trả về trạng thái `no-evidence` thay vì tự bịa. Nguồn được giữ trong lịch sử chat của phiên, và có thể xóa lịch sử mà không xóa hồ sơ/mentor yêu thích. Trạng thái online có trích dẫn **không chứng minh mức độ đúng ngữ nghĩa của mọi claim**.

### Tìm Mentor

Hệ thống tính hybrid score theo:

```text
65% TF-IDF cosine similarity
25% domain overlap
10% experience fit
```

Điểm được chặn trong khoảng 0–100 và ranking dùng tie-break ổn định để kết quả có tính tái lập. Có thể lọc theo lĩnh vực/loại hỗ trợ trước khi ranking; lọc không có kết quả sẽ hiển thị thông báo.

## Kiểm thử và chất lượng

Chạy toàn bộ kiểm tra local:

```bash
python -m py_compile app.py general_chat.py ui_helpers.py llm_client.py rag_engine.py matching_engine.py mentors_data.py mentor_data_diagnostics.py ingest.py scripts/evaluate_rag.py
python -m pytest -q
```

Chẩn đoán knowledge base:

```bash
python ingest.py
```

Chẩn đoán dữ liệu mentor và đánh giá retrieval offline:

```bash
python mentor_data_diagnostics.py
python -m scripts.evaluate_rag
```

Các tài liệu kiểm thử: [Test Plan](docs/TEST_PLAN.md), [UAT Checklist](docs/UAT_CHECKLIST.md), [RAG Evaluation](docs/RAG_EVALUATION.md), [Privacy & Dataflow](docs/PRIVACY_DATAFLOW.md).


GitHub Actions tự động chạy trên Pull Request và trên `main`:

- cài dependency từ môi trường sạch;
- quét pattern secret phổ biến trong tracked files;
- compile smoke check;
- regression tests bằng pytest;
- khởi động Streamlit thật và kiểm tra health endpoint;
- dựng từng sơ đồ Mermaid trong tài liệu kiến trúc thành SVG bằng trình duyệt headless để phát hiện lỗi cú pháp.

## Cấu trúc repository

```text
.
├── app.py                     # Streamlit presentation layer
├── general_chat.py            # Genuine multi-turn model API integration
├── ui_helpers.py              # Chat source + RAG mode helpers
├── profile_helpers.py         # Student profile validation and reset
├── llm_client.py              # Optional Groq infrastructure
├── rag_engine.py              # Retrieval + grounded answering
├── matching_engine.py         # Mentor scoring + explanation
├── mentors_data.py            # Validated in-memory MentorRepository + dataset
├── mentor_data_diagnostics.py # Offline mentor data diagnostics
├── ingest.py                  # Knowledge-base diagnostics
├── scripts/evaluate_rag.py    # Offline retrieval/refusal benchmark
├── knowledge_base/            # Markdown documents for RAG
├── tests/                     # Unit + smoke/regression tests
├── docs/                      # Canonical architecture.md + NFRs + process docs
├── .github/
│   ├── ISSUE_TEMPLATE/        # Customer request + bug report
│   ├── workflows/ci.yml       # CI quality gate
│   ├── CODEOWNERS             # Review ownership
│   └── pull_request_template.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── requirements.txt
└── .env.example
```

## Quy trình làm việc với GitHub Issues

Mọi yêu cầu mới bắt đầu từ một Issue có scope và acceptance criteria.

```text
Customer/Teacher Request
        ↓
      Issue
        ↓
  Feature/Fix Branch
        ↓
 Commit có Refs #ID
        ↓
   Pull Request
        ↓
  CI + Code Review
        ↓
      Merge
        ↓
 Issue tự đóng bằng Closes #ID
```

Ví dụ:

```bash
git checkout main
git pull
git checkout -b feat/issue-15-short-name

# sau khi sửa và test
git add path/to/file
git commit -m "feat: short description" -m "Refs #15"
git push -u origin feat/issue-15-short-name
```

Trong Pull Request dùng `Closes #15` khi toàn bộ acceptance criteria đã đạt.

Xem thêm: [CONTRIBUTING.md](CONTRIBUTING.md) và [Customer Feedback Workflow](docs/CUSTOMER_WORKFLOW.md).

## AI safety và giảm hallucination

Grounded AI Assistant áp dụng các cơ chế phòng thủ cơ bản:

- retrieval trước generation;
- relevance threshold;
- prompt yêu cầu chỉ dùng context;
- citation `[S1]`, `[S2]`, ... cho khẳng định quan trọng;
- no-evidence refusal;
- coi nội dung tài liệu là dữ liệu, không phải instruction;
- temperature thấp;
- fallback khi API lỗi hoặc thiếu key.

Đây là prototype học tập, vì vậy người dùng vẫn nên kiểm chứng thông tin quan trọng bằng nguồn gốc. **Chưa có kiểm định tự động citation/claim-level faithfulness**; các nguồn hiển thị là tài liệu được retrieval lấy ra, không phải chứng nhận mọi khẳng định đúng. Khi có Groq key và opt-in, lịch sử Trò chuyện AI, câu hỏi RAG/nguồn truy xuất hoặc hồ sơ matching có thể được gửi tới nhà cung cấp; không nhập dữ liệu riêng tư khi chưa được khách hàng phê duyệt xử lý.

## Nhóm phát triển

| Thành viên | Mã sinh viên | Workstream |
| --- | --- | --- |
| **Lê Văn Mạnh** | BAI250042 | Leader, AI/RAG, integration, review |
| Đỗ Văn Cường | BCS252484 | Backend, matching |
| Lê Hải Đăng | BAI250012 | Testing, CI/CD |
| Dương Tuấn Dũng | BIT250099 | Backend, data |
| Nguyễn Văn Phúc | BCS252351 | AI/RAG, QA |
| Hà Văn Dương | Chưa xác nhận | Frontend, Streamlit UX, Issues #50/#51 |
| Duy Anh | Chưa xác nhận | UAT scenarios, Issue #22 |

Bảng phân công mô tả workstream, không thay thế lịch sử commit/PR làm bằng chứng đóng góp cá nhân.

## Security và License

Không commit API key, token, password hoặc file `.env`. Xem [SECURITY.md](SECURITY.md).

Dự án phát hành theo [MIT License](LICENSE).

📋 **Bộ kiểm thử và ma trận truy vết (Testing):** [Testing handoff, 34 test cases, CI evidence](docs/TESTING_HANDOFF.md). Báo cáo JUnit/coverage nằm trong GitHub Actions artifacts theo từng commit SHA; UAT và live Groq cần kiểm thử riêng.
