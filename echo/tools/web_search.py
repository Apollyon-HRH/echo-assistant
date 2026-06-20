from __future__ import annotations

import re
from tools._shared import json_dump, normalize_url, http_get
from core.exceptions import ToolException

def web_search(query: str, num_results: int = 5, **kwargs) -> str:
    """
    Search the web using DuckDuckGo (via ddgs) and return structured results.
    Fallback para scraping HTML se a API falhar.
    """
    results = []

    # Tentativa 1: Usar a nova biblioteca ddgs (recomendada)
    try:
        from ddgs import DDGS  # nova biblioteca (antiga duckduckgo_search)
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=num_results):
                results.append({
                    "title": item.get("title", ""),
                    "href": item.get("href", ""),
                    "body": item.get("body", ""),
                })
        if results:
            return json_dump(results[:num_results])
    except ImportError:
        # Fallback para a biblioteca antiga (caso não tenha instalado o ddgs)
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for item in ddgs.text(query, max_results=num_results):
                    results.append({
                        "title": item.get("title", ""),
                        "href": item.get("href", ""),
                        "body": item.get("body", ""),
                    })
            if results:
                return json_dump(results[:num_results])
        except ImportError:
            pass
    except Exception as e:
        # Se a API falhar, parte para o fallback de scraping
        pass

    # Tentativa 2: Fallback com scraping do HTML do DuckDuckGo
    try:
        url = normalize_url(f"https://html.duckduckgo.com/html/?q={query}")
        html = http_get(url, timeout=20).text
        # Extrai links e títulos da página
        links = re.findall(
            r'nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>',
            html,
            flags=re.I | re.S
        )
        for href, title in links[:num_results]:
            clean_title = re.sub(r"<.*?>", "", title)
            clean_href = re.sub(r'^//', 'https://', href)
            results.append({
                "title": clean_title,
                "href": clean_href,
                "body": ""
            })
        if results:
            return json_dump(results[:num_results])
    except Exception as e:
        raise ToolException(f"Falha na busca web: {e}")

    # Se nada funcionou, levanta exceção
    raise ToolException(f"Nenhum resultado encontrado para '{query}' após todas as tentativas.")