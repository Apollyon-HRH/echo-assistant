from __future__ import annotations

import feedparser
from tools._shared import json_dump
from core.exceptions import ToolException

def rss(url: str, limit: int = 10, **kwargs) -> str:
    """Parse an RSS/Atom feed."""
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            items.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
            })
        return json_dump({"feed_title": feed.feed.get("title", ""), "items": items})
    except Exception as exc:
        raise ToolException(f"rss failed: {exc}")
