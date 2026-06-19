"""Slack webhook tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def slack(text: str, webhook_url: str | None = None, **kwargs) -> str:
    """Send a Slack webhook message."""
    try:
        import os, requests
        url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        if not url:
            raise ToolException("SLACK_WEBHOOK_URL missing")
        resp = requests.post(url, json={"text": text}, timeout=30)
        resp.raise_for_status()
        return "Slack message sent"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
