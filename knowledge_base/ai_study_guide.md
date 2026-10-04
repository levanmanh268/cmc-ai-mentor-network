# Gợi ý học tập và làm dự án AI

Tài liệu này là gợi ý học tập nội bộ cho prototype.

Khi bắt đầu một project AI, hãy xác định bài toán, dữ liệu đầu vào, metric đánh giá và baseline trước khi tối ưu mô hình. Với chatbot hoặc RAG, nên tạo một tập câu hỏi kiểm thử gồm câu có bằng chứng, câu không có bằng chứng và câu cố tình gây nhiễu.

Debug hệ thống AI nên tách từng tầng: ingestion, retrieval, prompt, model generation và giao diện. Nếu câu trả lời sai, trước tiên kiểm tra xem tài liệu đúng có được retrieval lấy ra hay không. Nếu retrieval sai thì sửa indexing hoặc query strategy trước khi chỉnh prompt.

Để giảm hallucination, có thể giảm temperature, yêu cầu câu trả lời chỉ dựa trên context, buộc hiển thị citation, thêm threshold relevance và có chế độ từ chối khi không tìm thấy bằng chứng.
