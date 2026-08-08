# TalentScreen AI

TalentScreen AI là ứng dụng hỗ trợ HR sàng lọc CV theo mô hình human-in-the-loop.
Hệ thống trích xuất bằng chứng từ CV, đánh giá theo rubric và đề xuất bước tiếp
theo; quyết định tuyển dụng cuối cùng luôn thuộc về HR.

## Tính năng chính

- Quản lý tài khoản HR, job, candidate và quyết định tuyển dụng.
- Upload CV định dạng PDF/DOCX.
- Trích xuất text và các field cơ bản bằng code, không dùng token LLM.
- Chia CV theo section như kinh nghiệm, kỹ năng, dự án và học vấn.
- Tạo embedding local bằng `sentence-transformers`.
- Retrieve top-k chunk theo từng tiêu chí rubric.
- Chỉ gửi các chunk liên quan đã ẩn danh tới LLM.
- Chọn OpenAI hoặc Gemini cho toàn bộ backend bằng biến môi trường.
- Trả kết quả JSON có score, gaps, câu hỏi phỏng vấn và evidence gắn với
  `chunk_id`.
- Mã hóa PII và nội dung CV khi lưu trong SQLite.
- Ghi audit log cho các thao tác quan trọng.

## Kiến trúc pipeline CV RAG

```text
PDF/DOCX
   │
   ▼
extraction.py       Đọc tài liệu và regex field, không gọi LLM
   │
   ▼
chunking.py         Chia theo section và semantic boundary
   │
   ▼
embedding.py        sentence-transformers chạy local
   │
   ▼
retrieval.py        Retrieve top-k chunk theo rubric
   │
   ▼
security_service.py Kiểm tra prompt injection và ẩn danh PII
   │
   ▼
llm_client.py       Gọi OpenAI hoặc Gemini với các chunk liên quan
   │
   ▼
Structured JSON     Score, recommendation, gaps và evidence
```

## Công nghệ

- Backend: Python, FastAPI, Pydantic, SQLite
- AI provider: OpenAI hoặc Google Gemini
- Local embedding: sentence-transformers, PyTorch
- Document parser: pypdf, python-docx
- Frontend: React, Vite

## Yêu cầu

- Python 3.11 trở lên
- Node.js 18 trở lên
- API key Gemini hoặc OpenAI
- Kết nối Internet trong lần đầu tải local embedding model

## Cài đặt backend

Tại thư mục gốc của dự án:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Nếu PowerShell không cho phép activate virtualenv:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Cấu hình môi trường

Tạo `.env` từ file mẫu:

```powershell
Copy-Item .env.example .env
```

### Sử dụng Gemini

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.5-flash

OPENAI_API_KEY=
OPENAI_CHAT_MODEL=gpt-4o-mini

LOCAL_EMBED_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### Sử dụng OpenAI

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o-mini

GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash

LOCAL_EMBED_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Bạn có thể cấu hình cả hai API key. Khi cần đổi provider, chỉ thay
`AI_PROVIDER=openai` hoặc `AI_PROVIDER=gemini`, sau đó khởi động lại backend.

Không commit file `.env` hoặc API key lên Git.

## Chạy backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app `
  --host 127.0.0.1 `
  --port 8000 `
  --reload
```

Các địa chỉ:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

Kiểm tra provider đang được sử dụng:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Ví dụ:

```json
{
  "status": "ok",
  "version": "2.0.0",
  "ai_provider": "Google Gemini",
  "ai_model": "gemini-3.5-flash"
}
```

## Chạy frontend

Mở terminal mới:

```powershell
cd .\vai-recruiter-web
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Truy cập `http://127.0.0.1:5173`.

## Tài khoản demo

```text
demo@vairecruiter.local / Demo@123
hr@vairecruiter.local   / HR@123456
```

Các tài khoản này chỉ dành cho môi trường development.

## Chạy thử CV RAG

### 1. Đăng nhập

```powershell
$loginBody = @{
  email = "demo@vairecruiter.local"
  password = "Demo@123"
} | ConvertTo-Json

$login = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/auth/login" `
  -ContentType "application/json" `
  -Body $loginBody

$token = $login.access_token
```

### 2. Upload CV

Thay đường dẫn bên dưới bằng file PDF hoặc DOCX thật:

```powershell
$uploadJson = curl.exe -s `
  -X POST "http://127.0.0.1:8000/cv/upload" `
  -H "Authorization: Bearer $token" `
  -F "cv=@D:\CVs\candidate.pdf"

$upload = $uploadJson | ConvertFrom-Json
$cvId = $upload.id
$upload
```

Upload không gọi LLM. Bước này chỉ parse, chunk, tạo embedding local và lưu dữ
liệu mã hóa. Lần đầu có thể mất vài phút để tải embedding model.

### 3. Phân tích với rubric mặc định

```powershell
$result = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/cv/$cvId/analyze" `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body "{}"

$result | ConvertTo-Json -Depth 10
```

### 4. Phân tích với rubric tùy chỉnh

```powershell
$rubricBody = @{
  top_k = 3
  rubric = @(
    @{
      id = "python"
      name = "Python"
      description = "Kinh nghiệm Python trong dự án production"
      weight = 50
    },
    @{
      id = "system_design"
      name = "System design"
      description = "Bằng chứng thiết kế hệ thống và quyết định kiến trúc"
      weight = 30
    },
    @{
      id = "delivery"
      name = "Delivery"
      description = "Bằng chứng triển khai, vận hành và đo lường kết quả"
      weight = 20
    }
  )
} | ConvertTo-Json -Depth 5

$result = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/cv/$cvId/analyze" `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body $rubricBody
```

## API chính

| Method       | Endpoint                      | Chức năng                                  |
| ------------ | ----------------------------- | -------------------------------------------- |
| `GET`      | `/health`                   | Kiểm tra backend, provider và model        |
| `POST`     | `/auth/login`               | Đăng nhập và lấy Bearer token           |
| `POST`     | `/auth/register`            | Tạo tài khoản HR                          |
| `GET/POST` | `/jobs`                     | Danh sách và tạo job                      |
| `GET/POST` | `/candidates`               | Quản lý candidate                          |
| `POST`     | `/candidates/upload`        | Upload và screening theo workflow candidate |
| `POST`     | `/candidates/{id}/rescreen` | Chạy lại đánh giá candidate             |
| `POST`     | `/cv/upload`                | Parse, chunk và embedding CV local          |
| `POST`     | `/cv/{id}/analyze`          | RAG theo rubric với provider đã chọn     |
| `PUT`      | `/candidates/{id}/decision` | Lưu quyết định của HR                   |
| `GET`      | `/analytics`                | Thống kê                                   |
| `GET`      | `/audit`                    | Audit log                                    |

Ngoại trừ health check và các route xác thực, API yêu cầu:

```http
Authorization: Bearer <access_token>
```

Xem thêm [README_API.md](README_API.md) hoặc Swagger UI tại `/docs`.

## Cấu trúc dự án

```text
api.py                 FastAPI routes
config.py              Cấu hình từ biến môi trường
database.py            SQLite schema, migration và transaction
security_service.py    Mã hóa, redact PII và prompt-injection guard
document_service.py    Parser PDF/DOCX
extraction.py           Extraction và regex field
chunking.py             Section-aware chunking
embedding.py            Local sentence-transformers embedding
retrieval.py            Rubric-driven retrieval
llm_client.py           OpenAI/Gemini structured-output client
schemas.py              Pydantic schema cho CV RAG
ai_service.py           Candidate assessment workflow
test_cv_pipeline.py     Smoke test cho các bước deterministic
vai-recruiter-web/      React/Vite frontend
```

## Bảo mật và quyền riêng tư

- CV chỉ được gửi tới LLM sau khi retrieve các chunk liên quan.
- Email, số điện thoại và các thuộc tính không liên quan được redact trước khi
  gọi provider.
- Nội dung CV, filename và field nhận diện được mã hóa khi lưu trong SQLite.
- Prompt-injection pattern trong CV bị từ chối trước khi gọi LLM.
- AI chỉ đưa ra `advance` hoặc `needs_review`; HR quyết định cuối cùng.
- Không lưu API key trong source code.

## Kiểm tra nhanh

Kiểm tra cú pháp:

```powershell
.\.venv\Scripts\python.exe -m compileall -q `
  api.py ai_service.py config.py database.py `
  extraction.py chunking.py embedding.py retrieval.py llm_client.py schemas.py
```

Kiểm tra dependency:

```powershell
.\.venv\Scripts\python.exe -m pip check
```

Chạy test nếu đã cài `pytest`:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q test_cv_pipeline.py
```

## Xử lý lỗi thường gặp

### `GEMINI_API_KEY is not configured`

Đặt `AI_PROVIDER=gemini`, thêm `GEMINI_API_KEY` vào `.env` và restart backend.

### `OPENAI_API_KEY is not configured`

Đặt `AI_PROVIDER=openai`, thêm `OPENAI_API_KEY` vào `.env` và restart backend.

### Upload đầu tiên mất nhiều thời gian

`sentence-transformers` đang tải model embedding local. Những lần sau model được
đọc từ cache.

### Đổi provider nhưng `/health` vẫn báo model cũ

Dừng Uvicorn và chạy lại. Cấu hình provider được đọc khi process backend khởi
động.

### CV không đọc được

Chỉ hỗ trợ PDF và DOCX có text. PDF scan dạng ảnh cần bổ sung OCR trước khi
upload.

## Lưu ý

TalentScreen AI là công cụ hỗ trợ ra quyết định, không phải hệ thống tự động
tuyển hoặc loại ứng viên. Kết quả cần được HR kiểm tra lại dựa trên evidence và
quy trình tuyển dụng của tổ chức.
