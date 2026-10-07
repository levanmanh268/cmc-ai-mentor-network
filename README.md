# CMC AI Mentor Network

[![CI](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/workflows/ci.yml/badge.svg)](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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
| Grounded AI Assistant | Truy xuất tài liệu Markdown bằng TF-IDF + cosine similarity trước khi sinh câu trả lời |
| Citation | Hiển thị nguồn và relevance score để người dùng kiểm chứng |
| No-evidence refusal | Từ chối suy diễn khi không tìm được bằng chứng đủ liên quan |
| Offline-safe mode | Không có Groq API key vẫn dùng được retrieval và fallback |
| Mentor Matching | Xếp hạng mentor bằng semantic similarity + domain overlap + experience fit |
| Explainable ranking | Hiển thị match score và lý do phù hợp |
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
                         └──────┬────────┬─────┘
                                │        │
                  hỏi đáp tài liệu      │ tìm mentor
                                │        │
                                v        v
                    ┌──────────────┐  ┌─────────────────┐
                    │ RAG Engine   │  │ Matching Engine │
                    │rag_engine.py │  │matching_engine.py│
                    └──────┬───────┘  └────────┬────────┘
                           │                    │
                           v                    v
                 knowledge_base/*.md      mentors_data.py
                           │
                           │ optional LLM generation
                           v
                       Groq API
```

Thiết kế ưu tiên ba thuộc tính chất lượng: **khả năng kiểm thử**, **khả năng giải thích** và **graceful degradation** khi dịch vụ LLM không khả dụng.

## Cách chạy nhanh

Yêu cầu: **Python 3.11+**.

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

Nếu không cấu hình key, ứng dụng vẫn chạy ở **offline grounded mode**.

### 5. Khởi động

```bash
streamlit run app.py
```

Mặc định Streamlit mở tại `http://localhost:8501`.

## Cách sử dụng

### Hồ sơ cá nhân

Điền năm học, lĩnh vực quan tâm, mục tiêu và giới thiệu ngắn. Hồ sơ này được dùng cho Mentor Matching.

### Grounded AI Assistant

Hỏi câu liên quan đến tài liệu trong `knowledge_base/`. Hệ thống:

1. chuẩn hóa câu hỏi;
2. truy xuất top-k chunks;
3. áp dụng relevance threshold;
4. chỉ gửi context đã truy xuất cho LLM;
5. hiển thị nguồn đã dùng.

Nếu retrieval không đủ bằng chứng, hệ thống trả về trạng thái `no-evidence` thay vì tự bịa.

### Tìm Mentor

Hệ thống tính hybrid score theo:

```text
65% semantic similarity
25% domain overlap
10% experience fit
```

Điểm được chặn trong khoảng 0–100 và ranking dùng tie-break ổn định để kết quả có tính tái lập.

## Kiểm thử và chất lượng

Chạy toàn bộ kiểm tra local:

```bash
python -m py_compile app.py rag_engine.py matching_engine.py mentors_data.py ingest.py
python -m pytest -q
```

Chẩn đoán knowledge base:

```bash
python ingest.py
```

GitHub Actions tự động chạy trên Pull Request và trên `main`:

- cài dependency từ môi trường sạch;
- quét pattern secret phổ biến trong tracked files;
- compile smoke check;
- regression tests bằng pytest;
- khởi động Streamlit thật và kiểm tra health endpoint.

## Cấu trúc repository

```text
.
├── app.py                     # Streamlit presentation layer
├── rag_engine.py              # Retrieval + grounded answering
├── matching_engine.py         # Mentor scoring + explanation
├── mentors_data.py            # Demo mentor dataset
├── ingest.py                  # Knowledge-base diagnostics
├── knowledge_base/            # Markdown documents for RAG
├── tests/                     # Unit + smoke/regression tests
├── docs/                      # Project/process documentation
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

Đây là prototype học tập, vì vậy người dùng vẫn nên kiểm chứng thông tin quan trọng bằng nguồn gốc.

## Nhóm phát triển

| Thành viên | Mã sinh viên | Workstream |
| --- | --- | --- |
| **Lê Văn Mạnh** | BAI250042 | Leader, AI/RAG, integration, review |
| Đỗ Văn Cường | BCS252484 | Backend, matching |
| Lê Hải Đăng | BAI250012 | Testing, CI/CD |
| Dương Tuấn Dũng | BIT250099 | Backend, data |
| Nguyễn Văn Phúc | BCS252351 | AI/RAG, QA |

Bảng phân công mô tả workstream, không thay thế lịch sử commit/PR làm bằng chứng đóng góp cá nhân.

## Security và License

Không commit API key, token, password hoặc file `.env`. Xem [SECURITY.md](SECURITY.md).

Dự án phát hành theo [MIT License](LICENSE).
