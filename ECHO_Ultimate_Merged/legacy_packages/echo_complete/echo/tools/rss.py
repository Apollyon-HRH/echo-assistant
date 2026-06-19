import feedparser

from core.exceptions import ToolException

def rss(url: str, max_items: int = 5) -> str:
    """Read an RSS or Atom feed."""
    try:
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            raise ToolException(f"Feed inválido: {feed.bozo_exception}")
        items = []
        for entry in feed.entries[:max_items]:
            items.append(f"- {entry.get('title','sem título')}\n  {entry.get('link','')}\n  {entry.get('summary','')[:300]}")
        return "\n\n".join(items) or "Sem itens no feed."
    except Exception as e:
        raise ToolException(f"Erro na ferramenta rss: {e}") from e
