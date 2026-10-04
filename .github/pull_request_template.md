## Related issue

Closes #

## Summary

Mô tả ngắn thay đổi và lý do.

## Acceptance criteria

- [ ] Yêu cầu khách hàng / issue đã được đáp ứng.
- [ ] Không có thay đổi ngoài phạm vi issue.

## Validation

- [ ] `python -m py_compile app.py rag_engine.py matching_engine.py mentors_data.py ingest.py`
- [ ] `python -m pytest -q`
- [ ] Đã smoke-test luồng người dùng liên quan.
- [ ] GitHub Actions xanh.

## Security & AI quality

- [ ] Không commit API key, password, token hoặc dữ liệu nhạy cảm.
- [ ] Nếu sửa RAG, đã kiểm tra câu có bằng chứng và câu không có bằng chứng.
- [ ] Nếu sửa LLM integration, vẫn có fallback khi API lỗi hoặc thiếu key.

## Customer review notes

Ghi lại điểm cần khách hàng/giảng viên xác nhận nếu có.
