"""RSS/Atom reader."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def rss(url: str, limit: int = 5, **kwargs) -> str:
    """Read RSS/Atom feeds."""
    try:
        import feedparser
        feed = feedparser.parse(normalize_url(url))
        items = []
        for entry in feed.entries[:limit]:
            items.append({
                "title": getattr(entry, "title", ""),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", ""),
                "summary": getattr(entry, "summary", ""),
            })
        return json_dump(items)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
