"""Slack webhook sender."""

from __future__ import annotations
import os
import requests

from tools._common import ToolException

def slack(text: str, webhook_url: str | None = None) -> str:
    """Send a message to a Slack webhook."""
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
    if not url:
        raise ToolException("Webhook do Slack ausente.")
    try:
        r = requests.post(url, json={"text": text}, timeout=30)
        r.raise_for_status()
        return f"Slack OK ({r.status_code})"
    except Exception as e:
        raise ToolException(f"Falha no slack: {e}")
