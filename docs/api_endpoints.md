# Danh sách API Endpoints - V-AI Recruiter

Tài liệu này liệt kê các API endpoints đang được sử dụng và định nghĩa trong hệ thống Backend (FastAPI) của dự án.

## 1. Các API đang được gọi trực tiếp từ Frontend (React)

Các API này được cấu hình proxy qua đường dẫn `/api/*` (trong `vite.config.js`) và gọi trực tiếp từ giao diện:

*   **`POST /api/auth/login`**: Đăng nhập (nằm trong `AuthScreen.jsx`).
*   **`POST /api/auth/register`**: Đăng ký tài khoản (nằm trong `AuthScreen.jsx`).
*   **`GET /api/jobs`**: Lấy danh sách các Job đang mở (nằm trong `Workspace.jsx`).
*   **`POST /api/jobs`**: Tạo mới một Job (nằm trong `Workspace.jsx`).
*   **`POST /api/candidates/upload`**: Tải file CV lên, trích xuất text trong bộ nhớ và tự động chạy luồng phân tích (nằm trong `Workspace.jsx`).

---

## 2. Các API khác được định nghĩa trên Backend (FastAPI)

Ngoài các API đã được tích hợp trên, hệ thống backend còn cung cấp các endpoints sau để quản lý và mở rộng các tính năng của dashboard:

### Quản lý Tài khoản (Auth & User)
*   **`GET /health`**: Kiểm tra trạng thái sức khỏe của server và thông tin AI Provider đang kích hoạt.
*   **`GET /auth/me`**: Lấy thông tin user hiện tại (yêu cầu token).

### Quản lý Dashboard & Analytics
*   **`GET /dashboard`**: Lấy số liệu tổng quan (số lượng job đang mở, số CV đã quét, phân bổ quyết định Pass/Hold/Reject).
*   **`GET /analytics`**: Lấy báo cáo thống kê chi tiết (điểm đánh giá trung bình, cao nhất, thấp nhất).
*   **`GET /audit`**: Lấy lịch sử log các hành động trên hệ thống (dùng cho tính năng Nhật ký đánh giá - Audit Log).

### Quản lý Ứng viên & Đánh giá AI
*   **`GET /candidates`**: Lấy danh sách ứng viên (có hỗ trợ lọc theo `job_id`, tìm kiếm tên/email, phân trang).
*   **`GET /candidates/{candidate_id}`**: Lấy chi tiết thông tin và kết quả đánh giá của một ứng viên cụ thể.
*   **`POST /candidates`**: Thêm ứng viên mới (dùng khi chỉ có text, không có file upload).
*   **`PATCH /candidates/{candidate_id}`**: Cập nhật thông tin cơ bản của ứng viên (Tên, Email).
*   **`POST /candidates/{candidate_id}/rescreen`**: Chạy lại luồng đánh giá AI cho một ứng viên (tính toán lại điểm số và nhận xét).
*   **`PUT /candidates/{candidate_id}/decision`**: Lưu quyết định cuối cùng của HR (Pass/Hold/Reject) và điểm số ghi đè (Override score).

### Luồng CV RAG (Truy xuất dựa trên từ khóa/Section - Mới)
*   **`POST /cv/upload`**: Upload CV, chia nhỏ thành các section và tạo embedding vector lưu cục bộ (Không gọi API LLM ở bước này).
*   **`POST /cv/{cv_id}/analyze`**: Trích xuất các section liên quan bằng Local Embedding và chỉ gửi các đoạn đó cho LLM để phân tích.

> **Ghi chú:** Backend FastAPI chạy ở cổng `8000`. Frontend Vite chạy ở cổng `5173` và tự động proxy các request `/api/` về `http://127.0.0.1:8000`.
