"""Safe in-memory text extraction for supported CV formats."""

from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from config import MAX_CV_BYTES

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}


class DocumentError(ValueError):
    pass


def extract_cv_text(filename: str, content_type: str | None, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".doc":
        raise DocumentError("DOC is not supported safely; please upload PDF or DOCX.")
    if suffix not in ALLOWED_EXTENSIONS or content_type not in ALLOWED_MIME_TYPES:
        raise DocumentError("Only PDF and DOCX files are accepted.")
    if not data or len(data) > MAX_CV_BYTES:
        raise DocumentError("CV must be between 1 byte and 10 MB.")
    try:
        if suffix == ".pdf":
            text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(data)).pages)
        else:
            text = "\n".join(paragraph.text for paragraph in Document(BytesIO(data)).paragraphs)
    except Exception as exc:
        raise DocumentError("The CV could not be read. Upload a valid, non-password-protected file.") from exc
    if len(text.strip()) < 30:
        raise DocumentError("The CV does not contain enough readable text.")
    return text.strip()
