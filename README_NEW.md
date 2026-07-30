# V-AI Recruiter

V-AI Recruiter là hệ thống tuyển dụng thông minh chạy cục bộ bằng Python, FastAPI và React/Vite. Ứng dụng hỗ trợ:

- Tạo job tuyển dụng
- Sàng lọc CV bằng AI/embedding
- Lưu quyết định HR và ghi audit log
- Xem thống kê dashboard cho tuyển dụng

## Công nghệ sử dụng

- Backend: Python, FastAPI, SQLite
- AI: OpenAI embeddings/chat hoặc chế độ mock khi chưa có API key
- Frontend: React + Vite

## Cài đặt

### 1. Backend

```powershell
cd d:\AI Thuc Chien\minihackathon
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Tạo file `.env` nếu cần dùng OpenAI:

```env
OPENAI_API_KEY=sk-...
```

### 2. Frontend

```powershell
cd d:\AI Thuc Chien\minihackathon\vai-recruiter-web
npm install
```

## Chạy ứng dụng

### Backend API

```powershell
cd d:\AI Thuc Chien\minihackathon
.\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
```

### Frontend

```powershell
cd d:\AI Thuc Chien\minihackathon\vai-recruiter-web
npm run dev -- --host 127.0.0.1 --port 5173
```

Mở:
- Frontend: http://127.0.0.1:5173
- API: http://127.0.0.1:8000/docs

## Tài khoản demo

- `demo@vairecruiter.local` / `Demo@123`
- `hr@vairecruiter.local` / `HR@123456`

## Cấu trúc thư mục chính

```text
api.py               # FastAPI backend
ai_service.py        # Embedding + phân tích CV
database.py          # SQLite schema và audit log
ui.py                # Streamlit workflow cũ
vai-recruiter-web/   # React/Vite frontend
```

## Lưu ý

- Nếu chưa cấu hình OpenAI API key, ứng dụng vẫn chạy ở chế độ mock để demo.
- Dữ liệu lưu trong file `talentscreen_local.db` ở thư mục gốc.
