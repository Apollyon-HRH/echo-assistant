from __future__ import annotations

import requests
from tools._shared import json_dump
from core.config import CONFIG
from core.exceptions import ToolException

def telegram(text: str, chat_id: str | None = None, **kwargs) -> str:
    """Send a Telegram message via Bot API."""
    try:
        token = CONFIG.get("env", {}).get("telegram_token", "")
        chat_id = chat_id or CONFIG.get("env", {}).get("telegram_chat_id", "")
        if not token or not chat_id:
            raise ToolException("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is not configured")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=30)
        r.raise_for_status()
        return json_dump(r.json())
    except Exception as exc:
        raise ToolException(f"telegram failed: {exc}")
