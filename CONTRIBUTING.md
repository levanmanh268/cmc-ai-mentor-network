# Contributing

## Nguyên tắc

Mỗi thay đổi phải trace được từ yêu cầu đến code bằng chuỗi:

**Issue -> Branch -> Commit -> Pull Request -> CI -> Review -> Merge**

Không commit trực tiếp vào `main` cho công việc tính năng hoặc sửa lỗi thông thường.

## 1. Tạo hoặc nhận Issue

Issue cần có:

- vấn đề hoặc yêu cầu
- acceptance criteria
- phạm vi
- label phù hợp: `bug`, `enhancement` hoặc `documentation`
- người phụ trách nếu đã xác định

Nếu yêu cầu đến từ khách hàng, giữ nguyên nhu cầu gốc trong issue và ghi rõ tiêu chí nghiệm thu.

## 2. Tạo branch

Quy ước gợi ý:

```text
feat/issue-12-short-name
fix/issue-13-short-name
docs/issue-14-short-name
test/issue-15-short-name
```

Branch luôn bắt đầu từ `main` mới nhất.

## 3. Sửa code có phạm vi

Chỉ sửa file liên quan issue. Trước commit:

```bash
git status
git diff
python -m py_compile app.py rag_engine.py matching_engine.py mentors_data.py ingest.py
python -m pytest -q
```

Nếu test fail, không commit kiểu "cho xong". Tìm nguyên nhân gốc, sửa, chạy lại đến khi xanh.

## 4. Commit

Commit message ngắn, có loại thay đổi và tham chiếu issue:

```bash
git commit -m "fix: handle empty knowledge base" -m "Refs #13"
```

Dùng `Refs #13` trong commit để trace nhưng chưa tự đóng issue.

Không đưa secret, API key, password hoặc file `.env` vào commit.

## 5. Pull Request

PR cần ghi:

- Summary
- cách kiểm thử
- rủi ro hoặc giới hạn
- `Closes #13` nếu PR hoàn tất issue

Không merge khi:

- CI đỏ
- chưa xử lý review
- diff chứa thay đổi ngoài phạm vi issue
- acceptance criteria chưa đạt

## 6. Review loop

Reviewer kiểm tra theo thứ tự:

1. Đúng yêu cầu khách hàng chưa?
2. Có regression hoặc crash path không?
3. Test có kiểm được lỗi thật không?
4. AI có fallback khi API lỗi/không có key không?
5. RAG có trả lời khi thiếu bằng chứng một cách an toàn không?
6. Có secret hoặc dữ liệu nhạy cảm trong diff không?

Nếu phát hiện lỗi, quay lại code, commit fix và chờ CI chạy lại. Chỉ merge sau vòng cuối xanh.

## 7. Sau merge

- xác nhận issue tự đóng nếu PR có `Closes #...`
- kiểm tra CI của `main`
- nếu khách hàng đổi yêu cầu, tạo issue mới thay vì sửa lịch sử issue đã hoàn tất
