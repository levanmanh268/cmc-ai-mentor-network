Hướng dẫn tạo:

Trong VS Code, nhìn sang bên trái (cột Explorer).
Click chuột phải vào tên thư mục dự án.
Chọn New File.
Gõ tên file:textREADME.mdNhấn Enter.
Click đúp vào file README.md vừa tạo để mở.
Xóa hết nội dung mặc định (nếu có), rồi dán toàn bộ nội dung dưới đây vào:

Markdown# CMC AI Mentor Network

Hệ thống ghép đôi Mentor - Sinh viên AI thông minh dành cho sinh viên Đại học CMC.

## 🚀 Cách chạy dự án

### 1. Cài đặt các thư viện
Mở Terminal và chạy lệnh:
```bash
pip install -r requirements.txt
2. Thiết lập API Key

Copy file .env.example thành .env
Mở file .env và dán Groq API Key của bạn vào.

3. Chạy ứng dụng
Bashstreamlit run app.py
✨ Tính năng chính

AI Assistant thông minh (sử dụng RAG)
AI Matching ghép đôi mentor tự động (Hybrid Scoring)
Lưu mentor yêu thích
Giao diện thân thiện

🛠 Công nghệ sử dụng

Streamlit
Groq (Llama-3.3-70B)
Sentence Transformers + ChromaDB
LangChain

👨‍💻 Tác giả
Lê Văn Mạnh
Sinh viên năm 1 - Ngành Trí tuệ Nhân tạo
Đại học CMC (CMCU)