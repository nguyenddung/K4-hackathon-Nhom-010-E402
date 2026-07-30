# TalentScreen AI

TalentScreen AI là trợ lý sàng lọc ứng viên Backend Developer theo mô hình human-in-the-loop. AI chỉ đưa ra đề xuất có bằng chứng; HR luôn là người quyết định cuối cùng.

## Luồng MVP

1. Đăng nhập hoặc đăng ký tài khoản HR Manager/Recruiter.
2. Truy cập pipeline theo phòng ban và từng Job đang tuyển.
3. Xem nhanh ứng viên theo match score, confidence và trạng thái HR.
4. Tạo Job và nhập JD làm nguồn đánh giá chuẩn.
5. Upload CV PDF/DOCX hoặc chọn ứng viên có sẵn.
6. Mở hồ sơ chi tiết để xem breakdown, evidence, gap và câu hỏi phỏng vấn.
7. HR đề xuất/chưa đề xuất, có thể override điểm và ghi lý do.
8. Theo dõi toàn bộ thay đổi trong audit log.

Frontend đã có dữ liệu Backend Developer mẫu để demo ngay. Quyết định và audit event mới được lưu trong trình duyệt; FastAPI cung cấp API thật cho đăng nhập, CV upload, AI assessment, quyết định và audit.

## Công nghệ sử dụng

- Backend: Python, FastAPI, SQLite (có thể nâng cấp PostgreSQL/pgvector)
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

## Tài khoản API demo

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

- Frontend dùng đăng nhập/đăng ký qua FastAPI; có sẵn tài khoản demo ở trên.
- Nếu chưa cấu hình OpenAI API key, backend vẫn chạy ở chế độ AI fallback để demo.
- Dữ liệu lưu trong file `talentscreen_local.db` ở thư mục gốc.
