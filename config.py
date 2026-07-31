"""Runtime configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "talentscreen_local.db"))
APP_ENV = os.getenv("APP_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-development-secret-before-production")
TOKEN_TTL_MINUTES = int(os.getenv("TOKEN_TTL_MINUTES", "480"))
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
MAX_CV_BYTES = 10 * 1024 * 1024

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").strip().casefold()
if AI_PROVIDER not in {"openai", "gemini"}:
    raise RuntimeError("AI_PROVIDER must be either 'openai' or 'gemini'")

# CHAT_MODEL remains supported for existing .env files.
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", os.getenv("CHAT_MODEL", "gpt-4o-mini"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2400"))
