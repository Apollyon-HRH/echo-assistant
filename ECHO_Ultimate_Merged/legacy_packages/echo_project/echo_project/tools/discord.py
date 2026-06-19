"""Discord webhook tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def discord(text: str, webhook_url: str | None = None, **kwargs) -> str:
    """Send a Discord webhook message."""
    try:
        import os, requests
        url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "")
        if not url:
            raise ToolException("DISCORD_WEBHOOK_URL missing")
        resp = requests.post(url, json={"content": text}, timeout=30)
        resp.raise_for_status()
        return "Discord message sent"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
