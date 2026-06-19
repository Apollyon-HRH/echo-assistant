from __future__ import annotations

import os
import requests

from tools._base import ToolException

def discord(text: str) -> str:
    """Send a message to a Discord webhook."""
    try:
        url = os.getenv("DISCORD_WEBHOOK_URL", "")
        if not url:
            raise ToolException("DISCORD_WEBHOOK_URL missing")
        r = requests.post(url, json={"content": text}, timeout=30)
        r.raise_for_status()
        return "sent"
    except Exception as e:
        raise ToolException(str(e)) from e
