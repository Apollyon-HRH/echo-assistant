from __future__ import annotations

import requests

from core.config import CONFIG
from core.exceptions import ToolException

def discord(content: str, webhook_url: str | None = None) -> str:
    """Send a message to a Discord webhook."""
    url = webhook_url or CONFIG.get("env", {}).get("discord_webhook_url")
    if not url:
        raise ToolException("Discord webhook URL not configured")
    try:
        r = requests.post(url, json={"content": content}, timeout=30)
        r.raise_for_status()
        return "Discord message sent"
    except Exception as exc:
        raise ToolException(f"discord failed: {exc}") from exc
