# TalentScreen AI

## What This Is

TalentScreen AI là ứng dụng web xây dựng bằng Streamlit hỗ trợ đội ngũ tuyển dụng (HR) tạo mô tả công việc (JD), sàng lọc và đánh giá CV ứng viên tự động dựa trên OpenAI API (hoặc chế độ MOCK khi không có API key), lưu trữ quyết định tuyển dụng và theo dõi lịch sử kiểm toán trong SQLite local database.

## Core Value

Tối ưu hóa quy trình sàng lọc hồ sơ ứng viên nhanh chóng, minh bạch và chính xác thông qua đối chiếu embedding và phân tích LLM, hỗ trợ HR đưa ra quyết định dựa trên dữ liệu.

## Business Context

- **Customer**: Đội ngũ Tuyển dụng / HR Teams / Hiring Managers.
- **Success Metric**: Tốc độ sàng lọc CV & tỷ lệ chính xác trong gợi ý câu hỏi phỏng vấn và phát hiện điểm thiếu sót.

## Requirements

### Validated

- ✓ Tạo vị trí tuyển dụng (Job JD) & tự động sinh embedding (`text-embedding-3-small` / MOCK fallback) — v1.0
- ✓ Sàng lọc CV ứng viên theo JD (tính Cosine Similarity & LLM analysis `gpt-4o-mini`) — v1.0
- ✓ Đánh giá & Phân tích chi tiết: Điểm số, Tóm tắt, Thiếu sót cần làm rõ, Gợi ý câu hỏi phỏng vấn — v1.0
- ✓ Quản lý quyết định HR (Pass / Hold / Reject) kèm ghi chú — v1.0
- ✓ Phân tích thống kê & Lịch sử audit log — v1.0
- ✓ Chế độ MOCK tự động khi không cấu hình `OPENAI_API_KEY` — v1.0

### Active

- [ ] Batch CV Upload: Sàng lọc nhiều CV cùng lúc cho một vị trí.
- [ ] Export Report: Xuất báo cáo đánh giá ứng viên dạng PDF/Excel.
- [ ] Custom Rubric: Tùy chỉnh tiêu chí đánh giá và trọng số phù hợp với từng vị trí.

### Out of Scope

- Tự động gửi email tới ứng viên — Tập trung hoàn toàn vào công cụ hỗ trợ ra quyết định tuyển dụng.
- Lưu trữ file CV binary trên Cloud S3 — Lưu trực tiếp text/metadata cục bộ SQLite để đảm bảo bảo mật và tinh gọn.

## Context

- Tech stack: Python 3.10+, Streamlit, NumPy, SQLite, OpenAI API.
- Kiến trúc modular với các module tách biệt: `app.py` (entry point), `ui.py` (UI logic), `ai_service.py` (embedding & LLM), `database.py` (SQLite schema & queries), `styles.py` (custom CSS & styling), `config.py` (environment setup).

## Constraints

- **Local First**: Dữ liệu lưu vết hoàn toàn tại SQLite (`talentscreen_local.db`).
- **Privacy & Safety**: Đảm bảo AI chỉ hỗ trợ phân tích, không quyết định thay thế HR.
- **Graceful Fallback**: Phải chạy mượt mà ngay cả ở chế độ MOCK mà không có API Key.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| SQLite Local DB | Tăng tốc độ demo hackathon, không cần setup db server phức tạp | ✓ Good |
| Cosine Similarity + GPT-4o-mini | Kết hợp giữa lọc nhanh vector và phân tích sâu ngôn ngữ tự nhiên | ✓ Good |
| Hybrid MOCK / Live AI Mode | Giúp thử nghiệm ứng dụng dễ dàng mà không bắt buộc có API Key ngay | ✓ Good |

---
*Last updated: 2026-07-30 after GSD initial setup*
