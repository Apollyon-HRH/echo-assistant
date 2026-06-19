from __future__ import annotations

import os
import requests

from tools._base import ToolException

def telegram(chat_id: str, text: str) -> str:
    """Send a Telegram message with a bot token."""
    try:
        token = os.getenv("TELEGRAM_TOKEN", "")
        if not token:
            raise ToolException("TELEGRAM_TOKEN missing")
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=30)
        r.raise_for_status()
        return "sent"
    except Exception as e:
        raise ToolException(str(e)) from e
