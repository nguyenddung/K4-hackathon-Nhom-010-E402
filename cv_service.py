"""Strict PDF validation, storage, and text extraction for candidate CVs."""

from __future__ import annotations

import hashlib
import io
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from config import CV_STORAGE_PATH, MAX_CV_PAGES, MAX_CV_SIZE_BYTES


PDF_MIME_TYPE = "application/pdf"


class PdfValidationError(ValueError):
    """Raised when an uploaded CV is not an acceptable PDF."""


@dataclass(frozen=True)
class ParsedPdf:
    text: str
    page_count: int
    parser_confidence: float
    parse_status: str
    sha256: str
    size_bytes: int


def _safe_original_name(filename: str) -> str:
    name = Path(filename).name
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:120] or "cv.pdf"


def validate_and_parse_pdf(filename: str, mime_type: str | None, content: bytes) -> ParsedPdf:
    """Validate extension/MIME/signature and extract text without persisting the file."""
    if not filename.lower().endswith(".pdf"):
        raise PdfValidationError("CV bắt buộc phải có định dạng .pdf.")
    if mime_type and mime_type.lower() != PDF_MIME_TYPE:
        raise PdfValidationError("MIME của file không phải application/pdf.")
    if not content.startswith(b"%PDF-"):
        raise PdfValidationError("File không có chữ ký PDF hợp lệ; không được đổi đuôi file khác thành .pdf.")
    if not content:
        raise PdfValidationError("File PDF rỗng.")
    if len(content) > MAX_CV_SIZE_BYTES:
        raise PdfValidationError(
            f"CV vượt quá dung lượng cho phép ({MAX_CV_SIZE_BYTES // (1024 * 1024)} MB)."
        )

    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content), strict=False)
    except Exception as exc:
        raise PdfValidationError("PDF bị hỏng hoặc không thể mở.") from exc

    if reader.is_encrypted:
        raise PdfValidationError("PDF có mật khẩu. Vui lòng gửi bản PDF không khóa.")
    page_count = len(reader.pages)
    if page_count == 0:
        raise PdfValidationError("PDF không có trang nội dung.")
    if page_count > MAX_CV_PAGES:
        raise PdfValidationError(f"CV vượt quá giới hạn {MAX_CV_PAGES} trang.")

    page_texts: list[str] = []
    readable_pages = 0
    for page in reader.pages:
        try:
            text = (page.extract_text() or "").strip()
        except Exception:
            text = ""
        if len(text) >= 30:
            readable_pages += 1
        page_texts.append(text)
    full_text = "\n\n".join(part for part in page_texts if part).strip()
    readable_ratio = readable_pages / page_count
    length_signal = min(len(full_text) / 800.0, 1.0)
    confidence = round((0.7 * readable_ratio) + (0.3 * length_signal), 3)
    status = "PARSED" if confidence >= 0.65 else "LOW_CONFIDENCE"

    return ParsedPdf(
        text=full_text,
        page_count=page_count,
        parser_confidence=confidence,
        parse_status=status,
        sha256=hashlib.sha256(content).hexdigest(),
        size_bytes=len(content),
    )


def persist_pdf(application_id: str, filename: str, content: bytes) -> str:
    """Persist a validated PDF under a generated name and return its absolute path."""
    storage = Path(CV_STORAGE_PATH).resolve()
    storage.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_original_name(filename)
    target = (storage / f"{application_id}-{uuid.uuid4().hex[:8]}-{safe_name}").resolve()
    if storage not in target.parents:
        raise PdfValidationError("Tên file PDF không an toàn.")
    target.write_bytes(content)
    return str(target)
