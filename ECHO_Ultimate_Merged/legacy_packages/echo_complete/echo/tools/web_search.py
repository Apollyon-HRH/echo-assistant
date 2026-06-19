
import json
from typing import List

import requests

from core.exceptions import ToolException


def web_search(query: str, num_results: int = 3) -> str:
    """Search the web and return a concise result list."""
    try:
        results = []
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for item in ddgs.text(query, max_results=num_results):
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("href", "") or item.get("link", ""),
                        "snippet": item.get("body", ""),
                    })
        except Exception:
            try:
                from googlesearch import search
                for url in search(query, num_results=num_results, lang="pt"):
                    results.append({"title": url, "link": url, "snippet": ""})
            except Exception:
                url = "https://html.duckduckgo.com/html/"
                resp = requests.post(url, data={"q": query}, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
                resp.raise_for_status()
                text = resp.text
                import re
                found = re.findall(
                    r'nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>.*?result__snippet">(.*?)</a>',
                    text,
                    re.S,
                )
                for link, title, snippet in found[:num_results]:
                    results.append({
                        "title": re.sub("<.*?>", "", title),
                        "link": link,
                        "snippet": re.sub("<.*?>", "", snippet),
                    })
        if not results:
            return "Nenhum resultado encontrado."
        lines = []
        for i, item in enumerate(results, 1):
            lines.append(
                f"{i}. {item['title']}\n   {item['link']}\n   {item.get('snippet','')}".strip()
            )
        return "\n\n".join(lines)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta web_search: {e}") from e
