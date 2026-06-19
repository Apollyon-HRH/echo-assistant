"""Web search tool using DuckDuckGo and Google fallback."""

from __future__ import annotations

from tools._common import ToolException, clamp_text


def web_search(query: str, num_results: int = 3) -> str:
    """Search the web and return formatted results."""
    if not query.strip():
        raise ToolException("Consulta vazia.")
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
            from googlesearch import search
            for url in search(query, num_results=num_results, lang="pt"):
                results.append({"title": url, "href": url, "body": ""})
        except Exception as e:
            raise ToolException(f"Falha na busca web: {e}")

    if not results:
        return "Nenhum resultado encontrado."

    out = []
    for i, r in enumerate(results, 1):
        out.append(
            f"{i}. {r['title']}\n   {r['href']}\n   {clamp_text(r['body'], 220)}"
        )
    return "\n".join(out)
