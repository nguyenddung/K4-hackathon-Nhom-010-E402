# TalentScreen AI — Hackathon Quick Mode (Streamlit)

Bản đơn giản 1 file, chạy local, dùng SQLite + OpenAI embeddings thật.

## Chạy nhanh

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-xxxx   # hoặc nhập trực tiếp trong sidebar app
streamlit run app.py
```

Mở trình duyệt tại http://localhost:8501

## 4 bước demo

1. **Tạo Job** — nhập JD, tự động tạo embedding (OpenAI `text-embedding-3-small`).
2. **Screen CV** — paste CV, tính cosine similarity với JD + nhận xét từ `gpt-4o-mini`.
3. **HR Quyết định** — Pass / Hold / Reject, lưu vào SQLite.
4. **Fairness / Audit** — thống kê điểm số, phân bố quyết định, log toàn bộ hành động.

## Ghi chú

- Nếu không có API key, app tự chuyển sang MOCK mode (embedding giả lập bằng numpy random có seed cố định theo text, nhận xét AI là placeholder) — demo vẫn chạy được không lỗi.
- Dữ liệu lưu trong file `talentscreen_local.db` (SQLite) cùng thư mục — không cần Docker/Postgres.
- Muốn reset demo: xoá file `talentscreen_local.db` rồi chạy lại.
