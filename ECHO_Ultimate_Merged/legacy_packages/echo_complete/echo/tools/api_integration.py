import os
from typing import Any

import requests

from core.exceptions import ToolException

def api_integration(service: str, query: str = "", limit: int = 5, **kwargs: Any) -> str:
    """Query common APIs such as GitHub, Reddit, Twitter/X, or YouTube."""
    try:
        service = service.lower().strip()
        headers = {"User-Agent": "ECHO/1.0"}
        if service == "github":
            token = os.getenv("GITHUB_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"
            url = f"https://api.github.com/search/repositories?q={requests.utils.quote(query)}&per_page={limit}"
            data = requests.get(url, headers=headers, timeout=30).json()
            items = data.get("items", [])
            return "\n".join(f"- {i['full_name']} ({i.get('html_url','')})" for i in items) or "Sem resultados."
        if service == "reddit":
            url = f"https://www.reddit.com/search.json?q={requests.utils.quote(query)}&limit={limit}"
            data = requests.get(url, headers=headers, timeout=30).json()
            posts = data.get("data", {}).get("children", [])
            return "\n".join(f"- {p['data'].get('title','')} ({p['data'].get('url','')})" for p in posts) or "Sem resultados."
        if service in {"youtube", "yt"}:
            key = os.getenv("YOUTUBE_API_KEY")
            if not key:
                raise ToolException("YOUTUBE_API_KEY não configurada")
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={requests.utils.quote(query)}&maxResults={limit}&key={key}"
            data = requests.get(url, timeout=30).json()
            items = data.get("items", [])
            return "\n".join(f"- {i['snippet']['title']} ({i['id'].get('videoId','')})" for i in items) or "Sem resultados."
        if service in {"twitter", "x"}:
            token = os.getenv("TWITTER_BEARER_TOKEN")
            if not token:
                raise ToolException("TWITTER_BEARER_TOKEN não configurado")
            headers["Authorization"] = f"Bearer {token}"
            url = f"https://api.twitter.com/2/tweets/search/recent?query={requests.utils.quote(query)}&max_results={min(limit,100)}"
            data = requests.get(url, headers=headers, timeout=30).json()
            tweets = data.get("data", [])
            return "\n".join(f"- {t.get('text','')[:200]}" for t in tweets) or "Sem resultados."
        raise ToolException(f"Serviço não suportado: {service}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta api_integration: {e}") from e
