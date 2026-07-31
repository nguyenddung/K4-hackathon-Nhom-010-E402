export const seedJobs = [
  {
    id: 'backend-senior',
    title: 'Senior Backend Developer',
    code: 'ENG-042',
    department: 'Platform Engineering',
    requirements: ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'Kubernetes', 'System design'],
  },
  {
    id: 'backend-mid',
    title: 'Backend Developer',
    code: 'ENG-038',
    department: 'Product Engineering',
    requirements: ['Python', 'REST API', 'PostgreSQL', 'Docker', 'Redis'],
  },
]

export const seedCandidates = [
  {
    id: 'an',
    jobId: 'backend-senior',
    name: 'Nguyễn Hoàng An',
    initials: 'NA',
    role: 'Backend Engineer · 4 năm KN',
    file: 'Nguyen_Hoang_An_CV.pdf',
    updated: '2 phút trước',
    score: 82,
    confidence: 87,
    summary: 'Ứng viên đáp ứng tốt nền tảng backend với Python, FastAPI và PostgreSQL. Kinh nghiệm triển khai production được mô tả rõ, nhưng chưa có bằng chứng trực tiếp về Kubernetes.',
    breakdown: [
      ['Kỹ năng', 35, 40],
      ['Kinh nghiệm', 20, 25],
      ['Dự án', 17, 20],
      ['Yếu tố khác', 10, 15],
    ],
    evidence: [
      { skill: 'Python', status: 'found', source: 'CV · Kỹ năng', quote: 'Sử dụng Python 3.10 xây dựng các dịch vụ backend trong 4 năm.' },
      { skill: 'FastAPI', status: 'found', source: 'CV · Dự án FinHub', quote: 'Thiết kế 12 REST API bằng FastAPI, xử lý trung bình 2M request/tháng.' },
      { skill: 'PostgreSQL', status: 'found', source: 'CV · Kinh nghiệm', quote: 'Tối ưu truy vấn PostgreSQL, giảm p95 latency từ 480ms xuống 190ms.' },
      { skill: 'Docker', status: 'found', source: 'CV · Kỹ năng', quote: 'Đóng gói và triển khai dịch vụ bằng Docker, GitHub Actions.' },
      { skill: 'Kubernetes', status: 'missing', source: 'Không tìm thấy trong CV', quote: 'Không đủ bằng chứng để đánh giá kinh nghiệm Kubernetes.' },
      { skill: 'System design', status: 'partial', source: 'CV · Dự án FinHub', quote: 'Có mô tả event-driven architecture nhưng chưa nêu quy mô và trade-off.' },
    ],
    gaps: [
      { title: 'Kubernetes', severity: 'Cần xác minh', text: 'JD yêu cầu kinh nghiệm vận hành Kubernetes; CV không đề cập công nghệ này.' },
      { title: 'System design ở quy mô lớn', severity: 'Thiếu bằng chứng', text: 'Có kiến trúc event-driven nhưng chưa mô tả tải, độ tin cậy hoặc quyết định đánh đổi.' },
    ],
    questions: [
      'Bạn đã từng triển khai ứng dụng bằng Kubernetes trong dự án thực tế chưa? Vai trò cụ thể của bạn là gì?',
      'Với hệ thống xử lý 10.000 request/giây, bạn sẽ thiết kế API và tầng dữ liệu như thế nào?',
      'Hãy kể về một sự cố production gần đây: bạn phát hiện, xử lý và ngăn tái diễn ra sao?',
    ],
  },
  {
    id: 'minh',
    jobId: 'backend-senior',
    name: 'Trần Đức Minh',
    initials: 'TM',
    role: 'Software Engineer · 3 năm KN',
    file: 'Tran_Duc_Minh_CV.pdf',
    updated: '18 phút trước',
    score: 71,
    confidence: 74,
    summary: 'Ứng viên có nền tảng Python và API phù hợp. CV thiếu số liệu về quy mô hệ thống, PostgreSQL và kinh nghiệm ownership ở production.',
    breakdown: [['Kỹ năng', 31, 40], ['Kinh nghiệm', 16, 25], ['Dự án', 15, 20], ['Yếu tố khác', 9, 15]],
    evidence: [
      { skill: 'Python', status: 'found', source: 'CV · Kỹ năng', quote: 'Python, Django, Celery.' },
      { skill: 'REST API', status: 'found', source: 'CV · Kinh nghiệm', quote: 'Phát triển API cho nền tảng thương mại điện tử.' },
      { skill: 'PostgreSQL', status: 'partial', source: 'CV · Kỹ năng', quote: 'Có liệt kê PostgreSQL nhưng không nêu thời gian hoặc phạm vi sử dụng.' },
      { skill: 'Kubernetes', status: 'missing', source: 'Không tìm thấy trong CV', quote: 'Không đủ bằng chứng để đánh giá.' },
    ],
    gaps: [
      { title: 'Vận hành production', severity: 'Cần xác minh', text: 'Chưa rõ mức độ ownership và kinh nghiệm xử lý sự cố.' },
      { title: 'Kubernetes', severity: 'Thiếu bằng chứng', text: 'Không tìm thấy bằng chứng trong CV.' },
    ],
    questions: [
      'Bạn chịu trách nhiệm đến đâu trong việc vận hành dịch vụ sau khi release?',
      'Bạn đã tối ưu PostgreSQL trong trường hợp thực tế nào?',
      'Bạn có kinh nghiệm với Kubernetes hoặc một nền tảng orchestration tương đương không?',
    ],
  },
  {
    id: 'linh',
    jobId: 'backend-senior',
    name: 'Lê Thuỳ Linh',
    initials: 'LL',
    role: 'Backend Developer · 5 năm KN',
    file: 'Le_Thuy_Linh_CV.pdf',
    updated: '1 giờ trước',
    score: 89,
    confidence: 92,
    summary: 'Hồ sơ có bằng chứng mạnh về Python, distributed systems và vận hành Kubernetes. Phù hợp cao với yêu cầu kỹ thuật của vị trí.',
    breakdown: [['Kỹ năng', 37, 40], ['Kinh nghiệm', 23, 25], ['Dự án', 18, 20], ['Yếu tố khác', 11, 15]],
    evidence: [
      { skill: 'Python & FastAPI', status: 'found', source: 'CV · Kinh nghiệm', quote: 'Tech lead nhóm 4 người phát triển microservices bằng Python, FastAPI.' },
      { skill: 'Kubernetes', status: 'found', source: 'CV · Dự án PayFlow', quote: 'Vận hành 18 services trên EKS, thiết lập autoscaling và observability.' },
      { skill: 'PostgreSQL', status: 'found', source: 'CV · Dự án PayFlow', quote: 'Thiết kế partitioning cho bảng giao dịch 800M records.' },
      { skill: 'Mentoring', status: 'partial', source: 'CV · Kinh nghiệm', quote: 'Có vai trò tech lead nhưng chưa mô tả hoạt động coaching.' },
    ],
    gaps: [{ title: 'Mentoring', severity: 'Cần xác minh', text: 'JD ưu tiên khả năng nâng tầm đội ngũ; CV mới nêu vai trò tech lead.' }],
    questions: [
      'Bạn đã giúp một thành viên trong nhóm phát triển năng lực như thế nào?',
      'Quyết định system design khó nhất ở PayFlow là gì và trade-off bạn chấp nhận?',
    ],
  },
  {
    id: 'phuong',
    jobId: 'backend-mid',
    name: 'Phạm Minh Phương',
    initials: 'PP',
    role: 'Backend Developer · 2 năm KN',
    file: 'Pham_Minh_Phuong_CV.pdf',
    updated: 'Hôm qua',
    score: 76,
    confidence: 81,
    summary: 'Ứng viên có nền tảng Python, REST API và PostgreSQL phù hợp cấp độ Middle. Cần xác minh thêm về Redis, monitoring và khả năng xử lý sự cố production.',
    breakdown: [['Kỹ năng', 33, 40], ['Kinh nghiệm', 18, 25], ['Dự án', 16, 20], ['Yếu tố khác', 9, 15]],
    evidence: [
      { skill: 'Python', status: 'found', source: 'CV · Kinh nghiệm', quote: 'Phát triển backend bằng Python, Django và FastAPI trong 2 năm.' },
      { skill: 'PostgreSQL', status: 'found', source: 'CV · Dự án Ecom', quote: 'Thiết kế schema và tối ưu index cho PostgreSQL.' },
      { skill: 'Docker', status: 'found', source: 'CV · Kỹ năng', quote: 'Docker, Docker Compose, CI/CD.' },
      { skill: 'Redis', status: 'missing', source: 'Không tìm thấy trong CV', quote: 'Không đủ bằng chứng để đánh giá kinh nghiệm Redis.' },
    ],
    gaps: [
      { title: 'Redis', severity: 'Thiếu bằng chứng', text: 'JD yêu cầu Redis nhưng CV không đề cập.' },
      { title: 'Production monitoring', severity: 'Cần xác minh', text: 'Chưa có bằng chứng về logging, metrics hoặc alerting.' },
    ],
    questions: [
      'Bạn đã dùng Redis cho bài toán nào và lựa chọn cấu trúc dữ liệu ra sao?',
      'Bạn theo dõi sức khoẻ một API trên production bằng những chỉ số nào?',
    ],
  },
]

export const initialAudit = [
  { id: 1, time: '10:32 · Hôm nay', actor: 'TalentScreen AI', action: 'Hoàn tất phân tích', detail: 'Nguyễn Hoàng An · 82/100 · Confidence 87%' },
  { id: 2, time: '10:31 · Hôm nay', actor: 'Hệ thống', action: 'Ẩn danh dữ liệu CV', detail: 'Đã loại bỏ 4 trường PII trước khi gửi tới AI' },
  { id: 3, time: '09:14 · Hôm nay', actor: 'Mai Anh (HR)', action: 'Tải lên hồ sơ', detail: 'Nguyễn Hoàng An · Senior Backend Developer' },
]

export const backendJd = `Tuyển Backend Developer. Yêu cầu: Python, FastAPI, REST API, PostgreSQL, Docker, Kubernetes, system design, tối ưu hiệu năng và vận hành production. Ứng viên cần mô tả rõ vai trò, thời gian sử dụng công nghệ, quy mô dự án và kết quả đo lường được.`
