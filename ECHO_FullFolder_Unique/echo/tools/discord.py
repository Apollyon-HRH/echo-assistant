from __future__ import annotations

import requests
from tools._shared import json_dump
from core.config import CONFIG
from core.exceptions import ToolException

def discord(text: str, webhook_url: str | None = None, **kwargs) -> str:
    """Send a Discord webhook message."""
    try:
        webhook_url = webhook_url or CONFIG.get("env", {}).get("discord_webhook_url", "")
        if not webhook_url:
            raise ToolException("DISCORD_WEBHOOK_URL is not configured")
        r = requests.post(webhook_url, json={"content": text}, timeout=30)
        r.raise_for_status()
        return json_dump({"sent": True, "status_code": r.status_code})
    except Exception as exc:
        raise ToolException(f"discord failed: {exc}")
