from __future__ import annotations

from tools._base import ToolException

def web_search(query: str, num_results: int = 3) -> str:
    """
    Search the web using DuckDuckGo first, then Google fallback.
    """
    results = []
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=num_results):
                title = item.get("title", "")
                href = item.get("href", item.get("url", ""))
                body = item.get("body", "")
                results.append(f"- {title}\n  {href}\n  {body}".strip())
    except Exception:
        try:
            from googlesearch import search as google_search
            for url in google_search(query, num_results=num_results):
                results.append(f"- {url}")
        except Exception as e:
            raise ToolException(f"web_search failed: {e}") from e
    return "\n".join(results) if results else "No results found."
