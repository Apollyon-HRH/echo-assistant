from __future__ import annotations

from typing import List

import requests

from core.exceptions import ToolException
from ._shared import json_pretty, normalize_text

def web_search(query: str, num_results: int = 3) -> str:
    """Search the web using DuckDuckGo first and Google as fallback."""
    query = query.strip()
    if not query:
        raise ToolException("query cannot be empty")

    results = []
    # Primary: duckduckgo_search if installed
    try:
        from duckduckgo_search import DDGS  # type: ignore
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=num_results):
                results.append({
                    "title": item.get("title"),
                    "url": item.get("href") or item.get("url"),
                    "snippet": item.get("body") or item.get("snippet"),
                    "source": "duckduckgo",
                })
    except Exception:
        pass

    # Fallback: googlesearch-python
    if not results:
        try:
            from googlesearch import search  # type: ignore
            for url in search(query, num_results=num_results, lang="pt"):
                results.append({
                    "title": url,
                    "url": url,
                    "snippet": "",
                    "source": "google",
                })
        except Exception:
            pass

    # Final fallback: HTML scrape of DDG
    if not results:
        try:
            r = requests.get("https://html.duckduckgo.com/html/", params={"q": query}, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select(".result__title a")[:num_results]:
                title = a.get_text(" ", strip=True)
                url = a.get("href", "")
                snippet_el = a.find_parent(class_="result").select_one(".result__snippet") if a.find_parent(class_="result") else None
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet_el.get_text(" ", strip=True) if snippet_el else "",
                    "source": "duckduckgo-html",
                })
        except Exception as exc:
            raise ToolException(f"web_search failed: {exc}") from exc

    return json_pretty(results)
