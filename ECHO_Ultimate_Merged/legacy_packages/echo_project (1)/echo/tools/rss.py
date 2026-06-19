"""RSS/Atom feed reader."""

from __future__ import annotations
import feedparser
from tools._common import ToolException, clamp_text


def rss(url: str, limit: int = 5) -> str:
    """Read a feed and return the latest entries."""
    feed = feedparser.parse(url)
    if getattr(feed, "bozo", False) and not feed.entries:
        raise ToolException("Não foi possível ler o feed.")
    out = [f"Feed: {getattr(feed.feed, 'title', 'sem título')}"]
    for entry in feed.entries[:limit]:
        title = getattr(entry, "title", "")
        link = getattr(entry, "link", "")
        summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        out.append(f"- {title}\n  {link}\n  {clamp_text(summary, 180)}")
    return "\n".join(out)
