from __future__ import annotations

from tools._base import ToolException

def rss(url: str, limit: int = 5) -> str:
    """Read RSS or Atom feeds."""
    try:
        import feedparser
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            items.append(f"- {entry.get('title', '')}\n  {entry.get('link', '')}")
        return "\n".join(items) if items else "No items."
    except Exception as e:
        raise ToolException(str(e)) from e
