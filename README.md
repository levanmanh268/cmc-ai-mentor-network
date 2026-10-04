# CMC AI Mentor Network

[![CI](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/workflows/ci.yml/badge.svg)](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/workflows/ci.yml)

CMC AI Mentor Network là prototype giáo dục AI của **Nhóm 6, môn Công nghệ phần mềm**. Sản phẩm kết hợp:

- **Grounded AI Assistant** hỏi đáp trên kho tài liệu Markdown bằng RAG nhẹ, có nguồn và chế độ từ chối khi thiếu bằng chứng.
- **Mentor Matching** xếp hạng mentor bằng hybrid score gồm TF-IDF similarity, domain overlap và experience fit.
- **Offline-safe mode** để sản phẩm vẫn chạy khi chưa có Groq API key hoặc API tạm lỗi.
- **GitHub Issues + Pull Requests + CI** làm quy trình tiếp nhận yêu cầu khách hàng, phát triển, review và regression test.

> Đây là project học tập. Dữ liệu mentor và tài liệu mẫu trong repository là dữ liệu demo, không phải thông tin hay chính sách chính thức của Đại học CMC.

## 1. Demo flow

1. Mở **Hồ sơ cá nhân** và điền năm học, lĩnh vực quan tâm, mục tiêu.
2. Mở **AI Assistant** và hỏi một câu liên quan đến tài liệu trong `knowledge_base/`.
3. Hệ thống truy xuất top chunks, hiển thị relevance score và nguồn đã dùng.
4. Nếu không có bằng chứng đủ liên quan, hệ thống từ chối suy diễn.
5. Mở **Tìm Mentor** để nhận top mentor cùng match score và phần giải thích.
6. Khi LLM offline, ranking và explanation deterministic vẫn hoạt động.

## 2. Kiến trúc

```text
User
  |
  v
Streamlit UI (app.py)
  |------------------------------|
  v                              v
RAG Engine                       Mentor Matching
(rag_engine.py)                  (matching_engine.py)
  |                              |
  v                              v
knowledge_base/*.md              mentors_data.py
  |                              |
  +---------- optional ----------+
             Groq API
```

### Grounded RAG

`rag_engine.py` đọc các file Markdown, chia chunk, tạo TF-IDF index và dùng cosine similarity để retrieval. Câu trả lời online bị ràng buộc chỉ dùng context được truy xuất, có chống prompt injection cơ bản và yêu cầu citation `[S1]`, `[S2]`.

Không có API key vẫn dùng được retrieval. Khi đó hệ thống trả các đoạn liên quan nhất thay vì tự bịa câu trả lời.

### Mentor Matching

`matching_engine.py` dùng ba thành phần dễ giải thích:

- 65% TF-IDF similarity
- 25% domain overlap
- 10% experience fit

Điểm cuối luôn được chặn trong khoảng 0 đến 100 và ranking có tie-break ổn định.

## 3. Cài đặt

Yêu cầu Python 3.11+.

```bash
git clone https://github.com/levanmanh268/cmc-ai-mentor-network.git
cd cmc-ai-mentor-network

python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Cài dependency:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Tạo file cấu hình local:

```bash
cp .env.example .env
```

Điền API key của riêng bạn vào `.env`:

```text
GROQ_API_KEY=your_key_here
```

Không commit file `.env`.

## 4. Chạy sản phẩm

```bash
streamlit run app.py
```

Chẩn đoán knowledge base:

```bash
python ingest.py
```

## 5. Chạy test

```bash
python -m py_compile app.py rag_engine.py matching_engine.py mentors_data.py ingest.py
python -m pytest -q
```

GitHub Actions tự chạy hai quality gates trên mỗi Pull Request vào `main`.

## 6. Quy trình Issue -> Branch -> Commit -> PR

Mọi thay đổi bắt đầu bằng GitHub Issue.

Ví dụ với issue `#12`:

```bash
git checkout main
git pull
git checkout -b feat/issue-12-short-name
```

Sau khi sửa:

```bash
git status
git diff
python -m pytest -q

git add path/to/changed-file
git commit -m "feat: short description" -m "Refs #12"
git push -u origin feat/issue-12-short-name
```

Trong Pull Request dùng `Closes #12` khi PR hoàn tất issue. Không merge khi CI fail hoặc review còn unresolved.

Chi tiết xem [CONTRIBUTING.md](CONTRIBUTING.md).

## 7. Workflow tiếp nhận yêu cầu khách hàng

Thầy/cô hoặc người đóng vai khách hàng có thể vào tab **Issues** và chọn:

- **Customer request** cho yêu cầu tính năng, thay đổi nghiệp vụ hoặc tiêu chí mới. Tự gán label `enhancement`.
- **Bug report** cho lỗi có thể tái hiện. Tự gán label `bug`.

Mỗi yêu cầu phải có acceptance criteria trước khi code. Sau đó nhóm tạo branch riêng, commit có `Refs #issue`, mở PR có `Closes #issue`, chờ CI xanh và review rồi mới merge.

## 8. Cấu trúc repository

```text
.
├── app.py
├── rag_engine.py
├── matching_engine.py
├── mentors_data.py
├── ingest.py
├── knowledge_base/
├── tests/
├── .github/
│   ├── workflows/ci.yml
│   └── ISSUE_TEMPLATE/
├── CONTRIBUTING.md
├── SECURITY.md
├── requirements.txt
└── .env.example
```

## 9. Nhóm 6

| Thành viên | Mã sinh viên | Workstream |
| --- | --- | --- |
| Lê Văn Mạnh | BAI250042 | Leader, AI/RAG, integration, review |
| Đỗ Văn Cường | BCS252484 | Backend, matching |
| Lê Hải Đăng | BAI250012 | Testing, CI/CD |
| Dương Tuấn Dũng | BIT250099 | Backend, data |
| Nguyễn Văn Phúc | BCS252351 | AI/RAG, QA |

Bảng trên mô tả phạm vi phối hợp của nhóm, không dùng để thay thế lịch sử commit hoặc bằng chứng đóng góp cá nhân.

## 10. Security

Repository từng chứa một credential trong lịch sử Git. Credential cũ phải được revoke/rotate. Xem [SECURITY.md](SECURITY.md).
