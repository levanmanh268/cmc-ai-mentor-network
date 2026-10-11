# Chạy CMC AI Mentor Network trên Windows

## Cách khởi động nhanh

1. Cài Python 3.11 trở lên từ https://www.python.org/downloads/ và chọn **Add Python to PATH** nếu trình cài đặt cho phép.
2. Tải hoặc clone repository và giải nén đầy đủ nếu tải ZIP.
3. Mở thư mục chứa `app.py`, `requirements.txt` và `run_windows.bat`.
4. Nhấp đúp **run_windows.bat**.
5. Chờ thiết lập `.venv` và cài thư viện lần đầu; phải có kết nối internet trong bước này.
6. Mở http://localhost:8501 nếu trình duyệt không tự bật.

`run_windows.bat` không yêu cầu kích hoạt virtual environment trong PowerShell, nên tránh lỗi Execution Policy thường gặp.

> LLM dùng Groq là tùy chọn. Không cần `.env` để chạy chế độ offline.

## Cách chạy bằng terminal

Mở PowerShell trong thư mục repository:

```powershell
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Nếu không có lệnh `py -3.11`, thử `py -3` hoặc `python` sau khi xác minh phiên bản >=3.11.

## Những lỗi thường gặp

| Thông báo/hiện tượng | Nguyên nhân khả dĩ | Cách xử lý |
| --- | --- | --- |
| `'python' is not recognized` / `py not found` | Python chưa cài/PATH chưa đúng | Cài Python 3.11+, mở lại terminal |
| Microsoft Store mở ra khi gõ `python` | App execution alias thay thế Python thật | Cài Python từ python.org hoặc dùng `py -3.11` |
| `running scripts is disabled on this system` | PowerShell chặn `Activate.ps1` | Không dùng activate; chạy `run_windows.bat` hoặc gọi `.venv\Scripts\python.exe` trực tiếp |
| `No module named streamlit` | Sai interpreter, chưa cài requirements | Chạy `.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| `Failed building wheel` / pip không tải được | Python/kiến trúc chưa tương thích, proxy, internet | Dùng Python 3.11 x64, cập nhật pip, kiểm tra mạng; gửi log nếu vẫn lỗi |
| Port 8501 busy | Streamlit đang chạy trước đó | Dừng tiến trình cũ hoặc chạy `python -m streamlit run app.py --server.port 8502` |
| AI trả về đoạn tài liệu thay vì câu trả lời | Chưa cấu hình API key | Đây là offline mode, không phải app crash |
| API/model call trả lỗi | Key chưa đúng/hết hạn, mạng hay provider lỗi | Xác minh API key được đặt trong `.env`, xem [SECURITY.md](../SECURITY.md) |
| RAG không thấy tài liệu mới | Cache nạp KB từ lúc app khởi động | Khởi động lại Streamlit sau khi cập nhật file Markdown |
| `git pull` báo local changes | Máy có sửa code chưa commit | Xem `git status`, lưu phần thay đổi trước khi cập nhật |

## Kiểm tra môi trường và gửi log

Trong PowerShell mở tại thư mục dự án:

```powershell
Get-Location
py -0p
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Nếu gặp lỗi, gửi **ảnh toàn bộ cửa sổ terminal hoặc đoạn traceback bắt đầu từ `Traceback` đến dòng cuối**. Gửi kèm lệnh đã thực thi và Python version. Che API key/password trước khi chia sẻ.

## Giới hạn của bài kiểm thử CI

CI kiểm tra source trên Linux và Windows bằng dependency install, pytest/UI testing và HTTP health check của Streamlit. Điều này **không đảm bảo** mọi máy Windows và mọi network đều hoạt động giống nhau, nên log tại máy người dùng vẫn cần để xử lý lỗi môi trường.
