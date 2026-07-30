# Roadmap: TalentScreen AI

## Overview

Dự án TalentScreen AI đã đạt mốc v1.0 (Core MVP). Các giai đoạn tiếp theo tập trung nâng cao trải nghiệm HR: tải hồ sơ hàng loạt (Batch Processing), xuất báo cáo (Exporting), tùy chỉnh bộ tiêu chí đánh giá (Custom Rubric), và tích hợp bộ lọc nâng cao.

## Milestones

- ✅ **v1.0 Core MVP** - Phases 1-3 (Shipped 2026-07-30)
- 🚧 **v1.1 Advanced Screening & Export** - Phases 4-5 (In progress)
- 📋 **v1.2 Analytics & Integration** - Phase 6 (Planned)

## Phases

<details open>
<summary>✅ v1.0 Core MVP (Phases 1-3) - SHIPPED 2026-07-30</summary>

### Phase 1: Core Engine & DB Foundation
**Goal**: Xây dựng SQLite schema, audit log, và tích hợp OpenAI embeddings / LLM fallback mock.
**Plans**: 2 plans

Plans:
- [x] 01-01: SQLite Schema (`database.py`) & Audit Log
- [x] 01-02: OpenAI API & Embedding Service (`ai_service.py`)

### Phase 2: User Interface & Screening Flow
**Goal**: Giao diện Streamlit tạo Job, nộp CV và hiển thị phân tích điểm số, thiếu sót, câu hỏi phỏng vấn.
**Plans**: 2 plans

Plans:
- [x] 02-01: UI Layout, Styles & Job Creation Tab (`ui.py`, `styles.py`)
- [x] 02-02: CV Screening Tab & Candidate Evaluation Detail (`ui.py`)

### Phase 3: Decision Management & Analytics Dashboard
**Goal**: Cho phép HR đưa ra quyết định (Pass/Hold/Reject) và xem dashboard phân tích.
**Plans**: 1 plan

Plans:
- [x] 03-01: HR Decision Tab & Audit Trail View (`ui.py`)

</details>

### 🚧 v1.1 Advanced Screening & Export (In Progress)

**Milestone Goal:** Tối ưu hóa năng suất HR bằng cách hỗ trợ xử lý CV hàng loạt và xuất báo cáo chuyên nghiệp.

#### Phase 4: Batch CV Upload & Bulk Screening
**Goal**: Cho phép nộp nhiều file CV cùng lúc cho một vị trí công việc và tiến hành sàng lọc tự động.
**Depends on**: Phase 3
**Success Criteria**:
  1. HR có thể upload nhiều file CV (.pdf, .txt, .docx) cùng lúc.
  2. Bảng tổng hợp xếp hạng tất cả CV nộp vào vị trí với điểm số tương quan.
**Plans**: 2 plans

Plans:
- [ ] 04-01: Multiple file upload handler & text extraction
- [ ] 04-02: Bulk screening execution & comparative candidate table

#### Phase 5: Export Evaluation Reports
**Goal**: Xuất báo cáo đánh giá ứng viên ra dạng PDF / Excel để chia sẻ với hiring manager.
**Depends on**: Phase 4
**Success Criteria**:
  1. HR có thể tải xuống file báo cáo chi tiết của 1 ứng viên hoặc danh sách tổng hợp.
**Plans**: 1 plan

Plans:
- [ ] 05-01: Report generation module (PDF/Excel) & download UI

### 📋 v1.2 Analytics & Integration (Planned)

#### Phase 6: Custom Rubrics & Advanced Filters
**Goal**: Tùy chỉnh trọng số đánh giá (Kỹ năng, Kinh nghiệm, Học vấn) và lọc nâng cao.
**Depends on**: Phase 5

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Core Engine & DB | v1.0 | 2/2 | Complete | 2026-07-30 |
| 2. UI & Screening Flow | v1.0 | 2/2 | Complete | 2026-07-30 |
| 3. Decision & Analytics | v1.0 | 1/1 | Complete | 2026-07-30 |
| 4. Batch CV Upload | v1.1 | 0/2 | Ready to plan | - |
| 5. Export Reports | v1.1 | 0/1 | Planned | - |
| 6. Custom Rubrics | v1.2 | 0/1 | Planned | - |
