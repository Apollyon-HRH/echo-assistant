from __future__ import annotations

import os
import requests

from tools._base import ToolException

def slack(text: str) -> str:
    """Send a message to a Slack webhook."""
    try:
        url = os.getenv("SLACK_WEBHOOK_URL", "")
        if not url:
            raise ToolException("SLACK_WEBHOOK_URL missing")
        r = requests.post(url, json={"text": text}, timeout=30)
        r.raise_for_status()
        return "sent"
    except Exception as e:
        raise ToolException(str(e)) from e
