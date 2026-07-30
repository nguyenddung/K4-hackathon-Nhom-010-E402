"""Application configuration and AI provider resolution."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = os.getenv("TALENTSCREEN_DB_PATH", str(PROJECT_ROOT / "talentscreen_local.db"))
CV_STORAGE_PATH = Path(os.getenv("TALENTSCREEN_CV_STORAGE", str(PROJECT_ROOT / "uploads" / "cv")))
MAX_CV_SIZE_BYTES = int(os.getenv("MAX_CV_SIZE_BYTES", str(8 * 1024 * 1024)))
MAX_CV_PAGES = int(os.getenv("MAX_CV_PAGES", "20"))
MAX_CV_REVISIONS = int(os.getenv("MAX_CV_REVISIONS", "2"))

AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").strip().lower()
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "auto").strip().lower()
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "450"))
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "60"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
).rstrip("/")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")

OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.6-flash")
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")


@dataclass(frozen=True)
class AIRuntime:
    provider: str
    api_key: str
    base_url: str
    model: str

    @property
    def configured(self) -> bool:
        return self.provider in {"mock", "local"} or bool(self.api_key)


def _chat_provider() -> str:
    if AI_PROVIDER != "auto":
        return AI_PROVIDER
    # A single populated key is all that is needed. This priority is documented
    # for the uncommon case where several keys are populated at once.
    if GEMINI_API_KEY:
        return "gemini"
    if GROQ_API_KEY:
        return "groq"
    if OPENAI_API_KEY:
        return "openai"
    return "mock"


def get_chat_runtime() -> AIRuntime:
    provider = _chat_provider()
    runtimes = {
        "gemini": AIRuntime("gemini", GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_CHAT_MODEL),
        "groq": AIRuntime("groq", GROQ_API_KEY, GROQ_BASE_URL, GROQ_CHAT_MODEL),
        "openai": AIRuntime("openai", OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_CHAT_MODEL),
        "mock": AIRuntime("mock", "", "", "mock"),
    }
    if provider not in runtimes:
        raise ValueError("AI_PROVIDER must be one of: auto, gemini, groq, openai, mock")
    return runtimes[provider]


def get_embedding_runtime() -> AIRuntime:
    provider = EMBEDDING_PROVIDER
    if provider == "auto":
        chat_provider = _chat_provider()
        provider = chat_provider if chat_provider in {"gemini", "openai"} else "local"

    runtimes = {
        "gemini": AIRuntime("gemini", GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_EMBED_MODEL),
        "openai": AIRuntime("openai", OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_EMBED_MODEL),
        "local": AIRuntime("local", "", "", "sha256-seeded-384"),
        "mock": AIRuntime("local", "", "", "sha256-seeded-384"),
    }
    if provider not in runtimes:
        raise ValueError("EMBEDDING_PROVIDER must be one of: auto, gemini, openai, local")
    return runtimes[provider]
