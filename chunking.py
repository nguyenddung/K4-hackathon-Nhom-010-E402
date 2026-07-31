"""Section-aware CV chunking that splits at semantic boundaries, not characters."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CVChunk:
    id: str
    section: str
    text: str


SECTION_ALIASES = {
    "summary": ("summary", "profile", "objective", "about", "tóm tắt", "mục tiêu", "giới thiệu"),
    "experience": ("experience", "employment", "work history", "kinh nghiệm", "quá trình công tác"),
    "skills": ("skills", "technical skills", "technologies", "kỹ năng", "công nghệ"),
    "projects": ("projects", "selected projects", "dự án"),
    "education": ("education", "academic", "học vấn", "giáo dục"),
    "certifications": ("certifications", "certificates", "chứng chỉ"),
    "achievements": ("achievements", "awards", "thành tích", "giải thưởng"),
    "languages": ("languages", "ngôn ngữ", "ngoại ngữ"),
}


def _heading(line: str) -> str | None:
    cleaned = re.sub(r"^[#*\-\s]+|[:\s]+$", "", line).casefold()
    if not cleaned or len(cleaned) > 60:
        return None
    for canonical, aliases in SECTION_ALIASES.items():
        if cleaned in aliases:
            return canonical
    # Unknown headings are accepted when explicitly marked with a colon.
    # Uppercase alone is not enough because candidate names are commonly uppercase.
    words = cleaned.split()
    if 1 <= len(words) <= 6 and line.rstrip().endswith(":"):
        return re.sub(r"\s+", "_", cleaned)
    return None


def _paragraphs(lines: list[str]) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                result.append("\n".join(current))
                current = []
            continue
        # Each substantial bullet/job entry is a useful retrieval boundary.
        if current and re.match(r"^(?:[-•▪◦]|\d+[.)])\s+", stripped):
            result.append("\n".join(current))
            current = []
        current.append(stripped)
    if current:
        result.append("\n".join(current))
    return result


def _pack(section: str, lines: list[str], max_words: int) -> list[tuple[str, str]]:
    packed: list[tuple[str, str]] = []
    current: list[str] = []
    word_count = 0
    for paragraph in _paragraphs(lines):
        paragraph_words = len(paragraph.split())
        if current and word_count + paragraph_words > max_words:
            packed.append((section, "\n\n".join(current)))
            current, word_count = [], 0
        current.append(paragraph)
        word_count += paragraph_words
    if current:
        packed.append((section, "\n\n".join(current)))
    return packed


def chunk_by_section(text: str, max_words: int = 220) -> list[CVChunk]:
    sections: list[tuple[str, list[str]]] = []
    section, lines = "profile", []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        detected = _heading(line)
        if detected:
            if any(item.strip() for item in lines):
                sections.append((section, lines))
            section, lines = detected, []
        else:
            lines.append(line)
    if any(item.strip() for item in lines):
        sections.append((section, lines))

    raw_chunks = [
        item
        for section_name, section_lines in sections
        for item in _pack(section_name, section_lines, max_words)
    ]
    return [
        CVChunk(id=f"chunk-{index:03d}", section=section_name, text=content)
        for index, (section_name, content) in enumerate(raw_chunks, start=1)
        if content.strip()
    ]
