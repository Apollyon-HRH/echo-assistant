"""Discord webhook sender."""

from __future__ import annotations
import os
import requests

from tools._common import ToolException

def discord(text: str, webhook_url: str | None = None) -> str:
    """Send a message to a Discord webhook."""
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "")
    if not url:
        raise ToolException("Webhook do Discord ausente.")
    try:
        r = requests.post(url, json={"content": text}, timeout=30)
        r.raise_for_status()
        return f"Discord OK ({r.status_code})"
    except Exception as e:
        raise ToolException(f"Falha no discord: {e}")
