from __future__ import annotations

import requests
from tools._shared import json_dump
from core.config import CONFIG
from core.exceptions import ToolException

def slack(text: str, webhook_url: str | None = None, **kwargs) -> str:
    """Send a Slack webhook message."""
    try:
        webhook_url = webhook_url or CONFIG.get("env", {}).get("slack_webhook_url", "")
        if not webhook_url:
            raise ToolException("SLACK_WEBHOOK_URL is not configured")
        r = requests.post(webhook_url, json={"text": text}, timeout=30)
        r.raise_for_status()
        return json_dump({"sent": True, "status_code": r.status_code})
    except Exception as exc:
        raise ToolException(f"slack failed: {exc}")
