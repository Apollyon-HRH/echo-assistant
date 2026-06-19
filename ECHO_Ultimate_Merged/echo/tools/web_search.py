from __future__ import annotations

from tools._shared import json_dump, normalize_url, http_get
from core.exceptions import ToolException

def web_search(query: str, num_results: int = 5, **kwargs) -> str:
    """Search the web and return structured results."""
    results = []
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=num_results):
                results.append({
                    "title": item.get("title", ""),
                    "href": item.get("href", ""),
                    "body": item.get("body", ""),
                })
    except Exception:
        try:
            url = normalize_url(f"https://html.duckduckgo.com/html/?q={query}")
            html = http_get(url, timeout=20).text
            import re
            links = re.findall(r'nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>', html, flags=re.I|re.S)
            for href, title in links[:num_results]:
                results.append({"title": re.sub(r"<.*?>", "", title), "href": href, "body": ""})
        except Exception as exc:
            raise ToolException(f"Web search failed: {exc}")
    return json_dump(results[:num_results])
