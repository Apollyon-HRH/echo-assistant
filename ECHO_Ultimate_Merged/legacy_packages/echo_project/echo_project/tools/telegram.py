"""Telegram messaging tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def telegram(chat_id: str, text: str, **kwargs) -> str:
    """Send a Telegram message using the Bot API."""
    try:
        import os
        import requests
        token = os.getenv("TELEGRAM_TOKEN", "")
        if not token:
            raise ToolException("TELEGRAM_TOKEN missing")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=30)
        resp.raise_for_status()
        return json_dump(resp.json())
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
