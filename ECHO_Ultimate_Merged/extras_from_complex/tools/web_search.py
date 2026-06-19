from __future__ import annotations
from duckduckgo_search import DDGS

def web_search(query: str, num_results: int = 5) -> str:
    items = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=num_results):
            items.append(f"- {r.get('title','')} :: {r.get('href','')}")
    return "\n".join(items) if items else "No results"
