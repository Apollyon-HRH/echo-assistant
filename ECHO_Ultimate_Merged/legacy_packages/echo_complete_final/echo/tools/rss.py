from __future__ import annotations

from core.exceptions import ToolException
from ._shared import json_pretty

def rss(url: str, limit: int = 10) -> str:
    """Read RSS/Atom feeds and return entries."""
    try:
        import feedparser  # type: ignore
    except Exception as exc:
        raise ToolException(f"feedparser not available: {exc}") from exc

    feed = feedparser.parse(url)
    if getattr(feed, "bozo", False) and not getattr(feed, "entries", None):
        raise ToolException(f"Invalid feed: {url}")

    results = []
    for entry in feed.entries[:limit]:
        results.append({
            "title": getattr(entry, "title", ""),
            "link": getattr(entry, "link", ""),
            "published": getattr(entry, "published", ""),
            "summary": getattr(entry, "summary", ""),
        })
    return json_pretty(results)
