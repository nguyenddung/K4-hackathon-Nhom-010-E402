# TalentScreen AI

Ứng dụng Streamlit hỗ trợ đội tuyển dụng tạo vị trí tuyển dụng, sàng lọc CV theo mô tả công việc (JD), lưu quyết định của HR và theo dõi lịch sử kiểm toán. Dự án chạy cục bộ với SQLite và hỗ trợ Gemini, Groq hoặc OpenAI qua cấu hình `.env`.

## Chức năng

1. **Hai cổng phân quyền**: Candidate và HR dùng chung backend nhưng chỉ thấy dữ liệu/chức năng đúng vai trò.
2. **Job & Rubric workflow**: `DRAFT_JOB → RUBRIC_REVIEW → JOB_APPROVED → JOB_PUBLISHED`; rubric phải có tổng trọng số 100%.
3. **CV PDF bắt buộc**: kiểm tra extension, MIME, signature, dung lượng, số trang, mật khẩu và parser confidence trước khi đưa vào queue.
4. **Sàng lọc có bằng chứng**: đối chiếu CV–JD hai lớp, lưu trích dẫn, confidence, gaps và routing an toàn, không auto reject.
5. **Human-in-the-loop**: HR chấm lại từng tiêu chí, lưu lý do override và audit before/after.
6. **Feedback, phỏng vấn và offer**: feedback phải được HR duyệt trước khi gửi; Candidate có thể nộp lại PDF, chọn lịch, nhận và phản hồi offer.

## Công nghệ

- Python, Streamlit và NumPy
- SQLite cho dữ liệu local
- `pypdf` để xác thực và đọc CV PDF
- Gemini, Groq hoặc OpenAI để phân tích JD/CV
- Gemini/OpenAI embedding; cấu hình Groq tự dùng local deterministic embedding

## Cài đặt và chạy

Yêu cầu: Python 3.10 trở lên và `pip`.

```powershell
git clone https://github.com/nguyenddung/TalentScreen_AI_Mini_Hackathon-.git
cd TalentScreen_AI_Mini_Hackathon-
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Mở `.env` và chỉ điền **một** API key. `AI_PROVIDER=auto` sẽ tự chọn Gemini, rồi Groq, rồi OpenAI theo key đang có.

Gemini:

```env
AI_PROVIDER=auto
GEMINI_API_KEY=your-gemini-api-key
```

Hoặc Groq:

```env
AI_PROVIDER=auto
GROQ_API_KEY=your-groq-api-key
```

Kiểm tra ứng dụng đã nhận cấu hình (lệnh này không in API key), rồi khởi động:

```powershell
python check_ai_config.py
python -m streamlit run app.py
```

Sau đó mở `http://localhost:8501` trong trình duyệt.

Nếu `.env` có nhiều key, đặt rõ `AI_PROVIDER=gemini`, `groq` hoặc `openai`. Khi dùng Groq, chat và đánh giá dùng Groq còn embedding mặc định dùng local. Có thể ép Gemini embedding bằng `EMBEDDING_PROVIDER=gemini` và điền thêm `GEMINI_API_KEY`.

## Chế độ MOCK

Ứng dụng vẫn chạy khi chưa có API key. Ở chế độ này, hệ thống dùng embedding local deterministic và hiển thị nhận xét mẫu để phục vụ demo. Điểm số và nhận xét trong MOCK mode không được dùng để đánh giá ứng viên thực tế. Có thể chọn rõ bằng `AI_PROVIDER=mock`.

## Dữ liệu local

Khi chạy lần đầu, ứng dụng tạo `talentscreen_local.db` ở thư mục gốc. File này lưu job, CV đã nhập, điểm số, quyết định và audit log; file được bỏ qua bởi Git.

File CV PDF được lưu dưới `uploads/cv/` (bị Git ignore); SQLite chỉ lưu metadata, checksum và đường dẫn. Database cũ được nâng cấp bằng migration version hóa, không cần xóa file DB.

## Kiểm thử

Chạy bộ test cô lập, không tác động `talentscreen_local.db`:

```powershell
python test_backend.py
```

Bộ test bao phủ migration từ schema cũ, RBAC, state machine, happy path đến hired, feedback và nộp lại PDF, Talent Pool consent, PDF giả mạo và smoke test ba trạng thái UI.

Để xóa toàn bộ dữ liệu demo, dừng ứng dụng và xóa file database:

```powershell
Remove-Item talentscreen_local.db
```

## Sử dụng AI có trách nhiệm

TalentScreen AI là công cụ hỗ trợ sàng lọc, không phải hệ thống ra quyết định tự động. Đội tuyển dụng cần xem xét thủ công mọi kết quả, kiểm chứng các thiếu sót được nêu và không sử dụng thông tin nhạy cảm như tuổi, giới tính, dân tộc, tôn giáo, tình trạng hôn nhân hoặc sức khỏe để đưa ra quyết định.

## Cấu trúc dự án

```text
app.py          # Điểm khởi động Streamlit
ui.py           # Các màn hình và luồng tương tác
ai_service.py   # Gemini/Groq/OpenAI, embedding và phân tích CV
check_ai_config.py # Kiểm tra provider/model mà không lộ API key
database.py     # SQLite schema và audit log
config.py       # Cấu hình ứng dụng
styles.py       # Giao diện Streamlit
```
