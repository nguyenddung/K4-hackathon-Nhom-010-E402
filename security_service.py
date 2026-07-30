"""Privacy and AI-security controls for candidate processing.

Only a redacted, injection-screened profile is ever passed to the AI provider.
"""

import base64
import hashlib
import hmac
import re
from dataclasses import dataclass

from cryptography.fernet import Fernet, InvalidToken

from config import SECRET_KEY


def _key() -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256((SECRET_KEY + ":pii").encode()).digest())


FERNET = Fernet(_key())


class SecurityViolation(ValueError):
    """Content must not proceed to the model."""


def encrypt(value: str | bytes) -> str:
    raw = value if isinstance(value, bytes) else value.encode("utf-8")
    return FERNET.encrypt(raw).decode("ascii")


def decrypt(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return FERNET.decrypt(value.encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeDecodeError):
        return None


def decrypt_bytes(value: bytes) -> bytes:
    return FERNET.decrypt(value)


def blind_index(value: str) -> str:
    """Deterministic keyed index; the original value cannot be recovered from it."""
    normalized = " ".join(value.casefold().split())
    return hmac.new((SECRET_KEY + ":blind-index").encode(), normalized.encode(), hashlib.sha256).hexdigest()


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d .()-]{7,}\d)(?!\d)")
ADDRESS_RE = re.compile(r"(?im)^(?:địa chỉ|dia chi|address|residence|quê quán|que quan)\s*[:\-].+$")
AGE_RE = re.compile(r"(?i)\b(?:\d{1,2}\s*(?:tuổi|years? old)|age\s*[:\-]?\s*\d{1,2})\b")
DEMOGRAPHIC_RE = re.compile(r"(?i)\b(?:nam|nữ|male|female|giới tính|gender|quốc tịch|nationality|dân tộc|ethnicity|tôn giáo|religion|tình trạng hôn nhân|marital status|vùng miền|quê quán)\s*[:\-]?\s*[^\n,;]{0,80}")
SCHOOL_RE = re.compile(r"(?im)^(?:trường|university|college|high school|đại học)\s*[:\-].+$")
INJECTION_RE = re.compile(r"(?i)(ignore\s+(?:all|any|previous|prior)\s+(?:instructions?|prompts?)|system\s*prompt|developer\s*message|jailbreak|act\s+as\s+(?:a\s+)?(?:system|assistant)|bỏ\s+qua\s+(?:mọi\s+)?(?:chỉ\s+dẫn|hướng\s+dẫn)|lệnh\s+hệ\s+thống|hãy\s+(?:cho|chấm)\s+(?:tôi\s+)?(?:điểm|10\s*điểm)|đánh\s+giá\s+tôi\s+100)" )


@dataclass(frozen=True)
class SafeText:
    text: str
    redactions: int


def reject_prompt_injection(text: str) -> None:
    if INJECTION_RE.search(text):
        raise SecurityViolation("CV contains content that attempts to influence the AI evaluation.")


def redact_for_ai(text: str) -> SafeText:
    """Remove PII and attributes unrelated to job capability before model use."""
    reject_prompt_injection(text)
    result, count = text, 0
    for pattern, replacement in ((EMAIL_RE, "[EMAIL_REDACTED]"), (PHONE_RE, "[PHONE_REDACTED]"), (ADDRESS_RE, "[ADDRESS_REDACTED]"), (AGE_RE, "[AGE_REDACTED]"), (DEMOGRAPHIC_RE, "[DEMOGRAPHIC_REDACTED]"), (SCHOOL_RE, "[SCHOOL_REDACTED]")):
        result, replacements = pattern.subn(replacement, result)
        count += replacements
    return SafeText(text=result[:50_000], redactions=count)
