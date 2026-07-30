"""Application configuration and environment loading."""

from dotenv import load_dotenv

load_dotenv()

DB_PATH = "talentscreen_local.db"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
MAX_OUTPUT_TOKENS = 450