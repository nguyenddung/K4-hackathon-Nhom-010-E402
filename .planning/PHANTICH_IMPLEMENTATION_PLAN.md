# Kế hoạch triển khai TalentScreen AI theo `phantich.md`

> **Trạng thái triển khai:** Hoàn tất P0–P9 ngày 2026-07-30. Schema hiện tại: v4. Bộ E2E và UI smoke test: PASS.

## 1. Mục tiêu và phạm vi

Xây dựng một MVP khép kín có hai cổng giao diện dùng chung một backend và một state machine:

- **Ứng viên (Candidate/User):** xem Job đã đăng, hỏi đáp sơ bộ, nộp CV, theo dõi trạng thái, bổ sung/nộp lại CV, nhận feedback đã được HR duyệt, chọn lịch phỏng vấn và xem kết quả được phép công khai.
- **HR/Admin:** tạo Job, duyệt rubric, theo dõi hàng đợi CV, xem scorecard có bằng chứng, ra quyết định human-in-the-loop, duyệt feedback, tạo lịch/câu hỏi, chấm phỏng vấn và đưa ra quyết định cuối.
- **Agent:** phân tích và đề xuất; không tự từ chối, tự gửi phản hồi tiêu cực hoặc tự ra quyết định tuyển dụng.

Ràng buộc đầu vào đã được chốt: **CV chỉ được gửi dưới dạng PDF**. Không nhận DOCX, TXT hoặc nội dung CV dán trực tiếp trong luồng chính thức.

Thiết kế phải bám ảnh tham chiếu trong `image/phantich/`: nền giấy kem, chữ serif đậm, chữ phụ monospace, mực đỏ, đường kẻ đen, card dạng giấy/chấm bài và bóng đổ cứng.

## 2. Kết quả kiểm tra hiện trạng (2026-07-30)

### 2.1 Đã có một phần

- Đăng nhập/đăng ký và phân nhánh giao diện theo role `HR`/`CANDIDATE`.
- AI phân tích JD, sinh rubric, đánh giá CV hai lớp, sinh feedback và câu hỏi phỏng vấn 5 cấp độ; có MOCK fallback.
- SQLite có code dự kiến lưu Job, ứng viên, quyết định, audit, feedback và dữ liệu phỏng vấn.
- Giao diện đã có token màu/typography gần style ảnh mẫu: `#F7F4EB`, `#221F1E`, `#C83827`, Playfair Display, Space Mono, card giấy và stamp badge.

### 2.2 Blocker phải sửa trước

1. **Dashboard HR và Candidate cùng crash sau đăng nhập:** `st.button(..., kind="secondary")` không phải tham số hợp lệ của Streamlit.
2. **Database đang dùng schema cũ:** `CREATE TABLE IF NOT EXISTS` không tự thêm cột. DB hiện thiếu các cột `jobs.status`, rubric, skills và hầu hết cột Candidate mới; thao tác tạo Job/nộp CV sẽ lỗi.
3. **Test backend không cô lập và không idempotent:** email/ID cố định làm lần chạy sau thất bại; test dừng ở bước 2/5 nên chưa xác nhận được hai luồng.
4. **State machine chỉ được dùng rời rạc:** Job nhảy thẳng sang `PUBLISHED`; hồ sơ nhảy thẳng sang `CV_ANALYZED`; mapping `NOT_PROCEEDING -> REJECTED` không khớp tài liệu.
5. **Candidate đang thấy điểm AI và routing nội bộ.** Theo nguyên tắc sản phẩm, Candidate chỉ nên thấy trạng thái/feedback đã được HR duyệt, không thấy xếp hạng nội bộ.
6. **CV chỉ dán text:** chưa upload PDF/DOCX, kiểm tra file, parser confidence, lỗi OCR hoặc hàng đợi/retry.
7. **Feedback chưa có duyệt/gửi:** nút sinh feedback ghi thẳng vào hồ sơ và Candidate thấy ngay; thiếu `FEEDBACK_GENERATED -> HR_APPROVED_FEEDBACK -> FEEDBACK_SENT`.
8. **Phỏng vấn chưa khép kín:** lịch đang hard-code ngày hiện tại 09:30; Candidate chưa chọn slot; HR chưa có UI chấm scorecard; chưa có next round/assessment/offer/final decision.
9. **Audit có ghi nhưng không có màn hình xem lịch sử**, chưa lưu actor và chuyển trạng thái trước/sau một cách đầy đủ.
10. **Chưa có visual regression:** mới đối chiếu CSS tĩnh, chưa có screenshot desktop/mobile để so với ảnh mẫu.

## 3. Kiến trúc đích

```text
app.py
  -> auth + route theo role
  -> candidate_views.py / hr_views.py
  -> services/
       application_service.py
       job_service.py
       interview_service.py
       feedback_service.py
       ai_service.py
  -> repositories/database.py
  -> SQLite + schema_migrations
```

Nguyên tắc:

- UI không tự viết SQL và không tự gán trạng thái.
- Mọi chuyển trạng thái đi qua service, kiểm tra role + transition hợp lệ và ghi audit trong cùng transaction.
- Chỉ Job `JOB_PUBLISHED` được trả về cho Candidate.
- AI trả kết quả có schema rõ ràng; service validate dữ liệu trước khi lưu.
- Nội dung do người dùng nhập phải được escape trước khi render bằng `unsafe_allow_html=True`.

## 4. Kế hoạch code theo từng hạng mục

### P0 — Khôi phục khả năng chạy và nền tảng test

**Việc làm**

- Thay `kind="secondary"` bằng API button hợp lệ.
- Thêm migration có version (`schema_migrations`) để nâng DB cũ lên schema mới mà không xóa dữ liệu.
- Thêm foreign keys, index và constraint cần thiết; bật `PRAGMA foreign_keys=ON` trên mỗi connection.
- Chuyển test sang DB tạm riêng qua cấu hình/fixture; dùng UUID/email ngẫu nhiên hoặc cleanup có kiểm soát.
- Thêm smoke test Streamlit cho ba trạng thái: chưa login, HR login, Candidate login.

**File dự kiến**

- `app.py`, `ui.py`, `database.py`, `config.py`, `test_backend.py`
- mới: `migrations.py`, `tests/conftest.py`, `tests/test_auth_routing.py`

**Nghiệm thu**

- Mở được cả hai dashboard, không có exception.
- Chạy test liên tiếp hai lần đều pass.
- DB cũ được nâng schema; dữ liệu cũ còn nguyên.

### P1 — Domain model, RBAC và state machine thống nhất

**Việc làm**

- Chuẩn hóa enum trạng thái Job, Application, Feedback, Interview và Offer đúng mục 15 của `phantich.md`.
- Tạo bảng `applications` tách khỏi `candidates`; một Candidate có thể nộp nhiều Job và nhiều revision.
- Thêm `actor_user_id`, `from_status`, `to_status`, `reason`, `created_at` vào audit event.
- Tạo transition guard. Ví dụ chỉ HR mới được `HR_REVIEW_PENDING -> SHORTLISTED`; Agent không có transition sang reject/hired.
- Candidate query luôn scope theo `current_user.id/email`; HR route bắt buộc role `HR`.
- Thay SHA-256 thuần bằng password hashing có salt phù hợp; không hiển thị tài khoản demo/mật khẩu ở production mode.

**Nghiệm thu**

- Transition trái phép bị từ chối và không ghi dữ liệu nửa chừng.
- Candidate A không đọc được hồ sơ của Candidate B.
- Audit tái dựng được toàn bộ timeline của một application.

### P2 — Luồng HR tạo Job và duyệt rubric (mục 2)

**Backend**

- Lưu đầy đủ: title, responsibilities, level, mandatory/preferred skills, experience, location/work mode, salary visibility, interview process, deadline, headcount.
- Flow: `DRAFT_JOB -> RUBRIC_REVIEW -> JOB_APPROVED -> JOB_PUBLISHED`.
- Rubric là dữ liệu chỉnh sửa được; validate tổng trọng số = 100; lưu version và người duyệt.
- AI chỉ đề xuất vague warnings, screening questions và interview structure.

**Giao diện HR**

- Wizard 4 bước: Thông tin Job → AI phân tích → HR sửa/duyệt rubric → Preview/Publish.
- Có nút Save draft, Back, Approve, Publish; không gộp duyệt và publish thành một thao tác.

**Nghiệm thu**

- Candidate không thấy draft/unapproved Job.
- Không publish được khi rubric chưa duyệt hoặc tổng weight khác 100.

### P3 — Luồng Candidate xem Job và nộp CV (mục 3–5)

**Backend**

- API/service danh sách Job chỉ lấy `JOB_PUBLISHED` và còn hạn.
- Chỉ nhận upload `.pdf`; kiểm tra đồng thời phần mở rộng, MIME `application/pdf` và file signature `%PDF-` để chặn file giả mạo bằng cách đổi tên.
- Áp dụng giới hạn dung lượng và số trang có cấu hình; lưu tên gốc, MIME, kích thước, SHA-256 checksum và đường dẫn file. MVP lưu file PDF local ngoài SQLite, database chỉ lưu metadata.
- Parser PDF trả `parse_status`, `parser_confidence`, page count, lỗi password/corrupt/thiếu trang và mức độ cần OCR đối với PDF scan.
- Lưu screening answers, portfolio links, contact info, start availability và work preference.
- Flow: `APPLICATION_SUBMITTED -> CV_QUEUED -> CV_PROCESSING -> CV_ANALYZED -> HR_REVIEW_PENDING`.
- Hỗ trợ revision; giới hạn số lần cập nhật cấu hình được và liên kết application gốc.

**Giao diện Candidate**

- Job detail có trách nhiệm, bắt buộc/ưu tiên, hình thức làm việc, quy trình/vòng phỏng vấn và SLA phản hồi.
- File uploader chỉ cho chọn PDF; bỏ text area dán CV khỏi luồng chính thức. Hiển thị tiến trình và lỗi file có hướng dẫn tải lại PDF hợp lệ.
- Timeline trạng thái thân thiện, không lộ AI score/ranking/routing nội bộ.

**Nghiệm thu**

- PDF hợp lệ và đọc tốt đi tới hàng đợi; file không phải PDF bị từ chối trước khi lưu; PDF có mật khẩu, hỏng, scan khó đọc hoặc confidence thấp đi nhánh upload lại/manual review.
- Candidate chỉ thấy hồ sơ thuộc tài khoản của mình.

### P4 — Queue, matching hai lớp và routing (mục 4–7)

**Việc làm**

- Tạo hàng đợi bền vững trong SQLite (`processing_jobs`) cho MVP; hỗ trợ lock, retry count, error message và reprocess.
- Lớp 1 chỉ gắn cờ điều kiện bắt buộc, không auto reject.
- Lớp 2 chấm từng rubric item với score, max score, exact evidence quote/location, gap và confidence.
- Validate tổng điểm, confidence range và bằng chứng không rỗng.
- Routing theo score + mandatory flags + missing data + parser confidence; không có `AUTO_REJECT`.
- Không đưa tuổi, giới tính, ảnh, hôn nhân, trường nổi tiếng hoặc khoảng trống nghề nghiệp vào scoring.

**Giao diện HR**

- Queue filter theo trạng thái/Job/priority/SLA; badge lỗi/retry/manual review.
- Màn hình split view: CV gốc bên trái, scorecard bên phải; click evidence sẽ nhấn đoạn CV tương ứng.

**Nghiệm thu**

- Mọi điểm có bằng chứng và confidence.
- Parser confidence thấp luôn được human review.
- Queue retry không tạo application trùng.

### P5 — HR review, quyết định và audit (mục 8, 17, 20)

**Việc làm**

- HR xem Agent score và ghi HR score theo từng tiêu chí, không chỉ một slider tổng.
- Các quyết định: `NEED_MORE_INFORMATION`, `SHORTLISTED`, `TALENT_POOL`, `NOT_PROCEEDING`, `FORWARD_TO_HIRING_MANAGER`, `REANALYZE_REQUESTED`.
- Bắt buộc lý do khi HR override Agent hoặc chọn không tiếp tục.
- Với talent pool phải có consent của Candidate.
- Audit UI hiển thị actor, thời gian, thay đổi điểm/trạng thái và lý do.

**Nghiệm thu**

- Lưu được cặp Agent/HR score, evidence và override reason theo criterion như JSON mẫu mục 20.
- Mọi quyết định tác động lớn đều truy ngược được người thực hiện.

### P6 — Feedback và vòng bổ sung CV (mục 9, luồng 2)

**Việc làm**

- Tách draft feedback khỏi bản được phép công khai.
- Flow: `HR_REJECTED/NEED_MORE_INFORMATION -> FEEDBACK_GENERATED -> HR_APPROVED_FEEDBACK -> FEEDBACK_SENT`.
- HR chỉnh sửa matched points, missing points, advice và before/after example trước khi approve.
- Candidate nhận feedback, bổ sung câu trả lời hoặc tạo CV revision rồi gửi lại để Agent đánh giá lại.
- Chặn dữ liệu cấm: ranking so với người khác, đặc điểm cá nhân, suy đoán tính cách, tiêu chí nội bộ.

**Nghiệm thu**

- Candidate không thấy feedback khi còn draft.
- Revision có version, giới hạn số lần và lịch sử đầy đủ.

### P7 — Shortlist, lịch và phỏng vấn (mục 10–14)

**Việc làm**

- HR tạo nhiều slot thật bằng date/time/format/interviewer/meeting link; Candidate chọn hoặc yêu cầu đổi.
- Flow: `SHORTLISTED -> INTERVIEW_INVITED -> INTERVIEW_SCHEDULED -> INTERVIEW_COMPLETED -> SCORECARD_PENDING -> INTERVIEWER_SUBMITTED -> AGENT_SUMMARIZED -> HR_DECISION`.
- Hiển thị/edit question bank 5 cấp độ; mỗi câu có competency, difficulty, good signal, probe signal, 0–4 scale và follow-up.
- Interviewer nhập điểm/ghi chú theo câu; Agent chỉ tổng hợp; HR chọn `NEXT_ROUND`, `ASSESSMENT_REQUIRED`, `OFFER_PENDING`, `TALENT_POOL`, `NOT_PROCEEDING`.
- Thêm offer status tối thiểu: pending/accepted/declined/expired/hired/closed.

**Nghiệm thu**

- Candidate tự chọn được một slot còn trống; transaction chống hai người giữ cùng slot.
- Không thể ra offer khi scorecard chưa hoàn tất và HR chưa xác nhận.

### P8 — Hoàn thiện style theo ảnh mẫu cho cả hai cổng

**Design tokens cố định**

- Paper `#F7F4EB`, card `#FAF7F0`, ink `#221F1E`, red `#C83827`, muted `#6E685F`, line `#D9D2C5`.
- Heading/logo: Playfair Display; body: Inter; label/index: Space Mono; Korean accent: Noto Serif KR.
- Border 1–2px, radius 3–4px, hard shadow 2–4px; tránh gradient và card bo tròn kiểu SaaS.

**Bố cục chung**

- Header full width gần ảnh: logo trái, nav theo vai trò ở giữa, tài khoản/CTA phải, double rule dưới header.
- Hero có kicker monospace đỏ, title serif lớn, từ khóa italic đỏ, CTA đen và secondary outline.
- Desktop max-width khoảng 1140px; tablet/mobile chuyển cột, tab cuộn ngang, không overflow.
- HR dùng cùng design system nhưng mật độ thông tin cao hơn; Candidate ưu tiên timeline và action rõ ràng.

**Visual QA**

- Chụp baseline tại 1440×900, 1024×768 và 390×844 cho: login, HR dashboard, Job wizard, queue detail, Candidate Job detail, application timeline, feedback, interview.
- So sánh màu, font, khoảng cách, header, button, card, border/shadow và trạng thái hover/focus/disabled.
- Kiểm tra contrast, keyboard focus, label form và zoom 200%.

**Nghiệm thu**

- Không còn Streamlit chrome/sidebar thừa; không có scroll ngang ở 390px.
- Hai cổng nhận diện cùng thương hiệu nhưng nav/action đúng role.
- Screenshot review được duyệt ở cả desktop và mobile trước khi chốt.

### P9 — E2E cho bốn luồng nghiệp vụ (mục 16) và release gate

**Test bắt buộc**

1. Happy path: HR publish Job → Candidate nộp → Agent đánh giá → HR shortlist → Candidate chọn lịch → scorecard → offer → hired.
2. CV cần cải thiện: HR yêu cầu bổ sung → duyệt feedback → Candidate cập nhật → Agent re-evaluate.
3. Talent pool: HR đề xuất → Candidate consent → lưu pool → liên kết Job mới.
4. Ngoại lệ: file lỗi/confidence thấp/AI timeout → manual review hoặc retry, không auto reject.

Riêng đầu vào CV phải có test: PDF text hợp lệ, PDF scan, PDF có mật khẩu, PDF hỏng, file khác đổi đuôi `.pdf`, file vượt dung lượng và PDF vượt số trang cho phép.

**Release gate**

- Unit tests: transition guard, scoring/routing, parser validation, RBAC.
- Integration tests: migration DB cũ, transaction + audit, MOCK/OpenAI error fallback.
- Streamlit AppTest: auth và component/action quan trọng của cả hai role.
- Visual regression: đủ các màn hình P8.
- Test chạy hai lần liên tiếp, không phụ thuộc dữ liệu trong `talentscreen_local.db`.

## 5. Thứ tự triển khai đề xuất

| Sprint | Phạm vi | Phụ thuộc | Kết quả bàn giao |
|---|---|---|---|
| 1 | P0 + P1 | Không | App chạy, DB migrate, RBAC/state machine/test nền |
| 2 | P2 + P3 | Sprint 1 | HR publish Job và Candidate nộp CV thật |
| 3 | P4 + P5 | Sprint 2 | Queue, scorecard bằng chứng, HR decision/audit |
| 4 | P6 + P7 | Sprint 3 | Feedback/revision và phỏng vấn khép kín |
| 5 | P8 + P9 | Sprint 1–4 | UI đúng style và E2E đủ bốn luồng |

Không nên bắt đầu pixel polish trước khi hoàn tất P0–P1, vì hiện tại dashboard và schema backend còn chặn toàn bộ luồng.

## 6. Definition of Done chung

- Hai role đăng nhập và chỉ thấy đúng dữ liệu/chức năng của mình.
- Hai portal dùng cùng backend state machine; reload không làm mất trạng thái.
- Candidate luôn biết trạng thái công khai hiện tại; HR luôn thấy lý do/bằng chứng của Agent.
- Candidate chỉ có thể gửi CV PDF đã vượt qua kiểm tra extension + MIME + signature + giới hạn dung lượng/trang.
- Không có quyết định từ chối/tuyển dụng hoặc feedback tiêu cực được AI tự thực hiện.
- Mọi mutation quan trọng có audit actor + before/after + reason + timestamp.
- MOCK mode chạy hết E2E không cần API key; lỗi AI không làm mất dữ liệu.
- UI vượt smoke/accessibility/responsive/visual regression ở các viewport quy định.
- Toàn bộ test pass trên DB tạm sạch và khi migration từ schema DB hiện tại.
