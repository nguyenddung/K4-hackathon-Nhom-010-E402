# TalentScreen AI

Ứng dụng Streamlit hỗ trợ đội tuyển dụng tạo vị trí tuyển dụng, sàng lọc CV theo mô tả công việc (JD), lưu quyết định của HR và theo dõi lịch sử kiểm toán. Dự án chạy hoàn toàn cục bộ với SQLite; khi cấu hình OpenAI API key, ứng dụng dùng embedding và mô hình chat để hỗ trợ đối chiếu hồ sơ.

## Chức năng

1. **Tạo job**: nhập tên vị trí và JD; hệ thống lưu embedding của JD.
2. **Sàng lọc CV**: đối chiếu CV với JD bằng cosine similarity, sau đó tạo tóm tắt, điểm phù hợp, các nội dung cần xác minh và câu hỏi phỏng vấn.
3. **Quyết định tuyển dụng**: HR chọn Pass, Hold hoặc Reject và lưu ghi chú; quyết định mới nhất có thể được cập nhật.
4. **Phân tích và kiểm toán**: xem thống kê điểm số, phân bố quyết định và lịch sử thao tác.

## Công nghệ

- Python, Streamlit và NumPy
- SQLite cho dữ liệu local
- OpenAI `text-embedding-3-small` để tạo embedding
- OpenAI `gpt-4o-mini` để phân tích CV

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

Mở `.env` và đặt khóa OpenAI của bạn:

```env
OPENAI_API_KEY=sk-...
```

Khởi động ứng dụng:

```powershell
streamlit run app.py
```

Sau đó mở `http://localhost:8501` trong trình duyệt.

## Chế độ MOCK

Ứng dụng vẫn chạy khi chưa có `OPENAI_API_KEY`. Ở chế độ này, hệ thống dùng embedding mô phỏng và hiển thị nhận xét mẫu để phục vụ demo. Điểm số và nhận xét trong MOCK mode không được dùng để đánh giá ứng viên thực tế.

## Dữ liệu local

Khi chạy lần đầu, ứng dụng tạo `talentscreen_local.db` ở thư mục gốc. File này lưu job, CV đã nhập, điểm số, quyết định và audit log; file được bỏ qua bởi Git.

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
ai_service.py   # OpenAI, embedding và phân tích CV
database.py     # SQLite schema và audit log
config.py       # Cấu hình ứng dụng
styles.py       # Giao diện Streamlit
```
