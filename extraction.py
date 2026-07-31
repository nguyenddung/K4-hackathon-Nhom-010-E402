"""Token-free CV extraction and deterministic field parsing."""

from __future__ import annotations

import re
from typing import Any

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?84|0)?[\s.-]?(?:\d[\s().-]?){8,11}(?!\d)")
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Z0-9_%./-]+", re.I)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[A-Z0-9_.-]+", re.I)
YEAR_RE = re.compile(r"\b(\d{1,2})\s*\+?\s*(?:năm|nam|years?|yrs?)\b", re.I)


def extract_document(filename: str, content_type: str | None, data: bytes) -> str:
    """Read a supported document without sending its contents to an LLM."""
    # Keep parser dependencies lazy so regex/chunk/retrieval stages remain independently testable.
    from document_service import extract_cv_text

    return extract_cv_text(filename, content_type, data)


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(0).strip() if match else None


def _candidate_name(text: str) -> str | None:
    ignored = re.compile(
        r"(?i)curriculum|resume|cv\b|profile|hồ sơ|thông tin|contact|email|phone|điện thoại"
    )
    for raw_line in text.splitlines()[:15]:
        line = " ".join(raw_line.split()).strip(" |:-")
        if (
            2 <= len(line.split()) <= 7
            and len(line) <= 80
            and not ignored.search(line)
            and not EMAIL_RE.search(line)
            and not PHONE_RE.search(line)
            and not re.search(r"https?://|www\.", line, re.I)
        ):
            return line
    return None


def extract_regex_fields(text: str) -> dict[str, Any]:
    """Extract high-confidence fields; missing values stay null instead of being guessed."""
    years = [int(value) for value in YEAR_RE.findall(text)]
    return {
        "name": _candidate_name(text),
        "email": _first_match(EMAIL_RE, text),
        "phone": _first_match(PHONE_RE, text),
        "linkedin": _first_match(LINKEDIN_RE, text),
        "github": _first_match(GITHUB_RE, text),
        "years_experience_claimed": max(years) if years else None,
    }


__all__ = ["extract_document", "extract_regex_fields"]
