"""Print safe AI configuration diagnostics (never prints API keys)."""

import json

from ai_service import get_ai_runtime_info


if __name__ == "__main__":
    info = get_ai_runtime_info()
    print(json.dumps(info, ensure_ascii=False, indent=2))
    if not info["chat_configured"]:
        raise SystemExit("AI provider đã chọn nhưng chưa có API key tương ứng trong .env")
