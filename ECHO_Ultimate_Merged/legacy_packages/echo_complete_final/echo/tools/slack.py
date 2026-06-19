from __future__ import annotations

import requests

from core.config import CONFIG
from core.exceptions import ToolException

def slack(text: str, webhook_url: str | None = None) -> str:
    """Send a message to a Slack webhook."""
    url = webhook_url or CONFIG.get("env", {}).get("slack_webhook_url")
    if not url:
        raise ToolException("Slack webhook URL not configured")
    try:
        r = requests.post(url, json={"text": text}, timeout=30)
        r.raise_for_status()
        return "Slack message sent"
    except Exception as exc:
        raise ToolException(f"slack failed: {exc}") from exc
