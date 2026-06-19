from __future__ import annotations

import os
import requests

from tools._base import ToolException

def api_integration(service: str, query: str = "", limit: int = 5) -> str:
    """Generic API integration for common platforms."""
    service = service.lower()
    try:
        if service == "github":
            token = os.getenv("GITHUB_TOKEN", "")
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            r = requests.get(f"https://api.github.com/search/repositories?q={query}&per_page={limit}", headers=headers, timeout=30)
            r.raise_for_status()
            items = r.json().get("items", [])
            return "\n".join(f"- {i['full_name']} ({i['html_url']})" for i in items)
        if service == "reddit":
            client_id = os.getenv("REDDIT_CLIENT_ID", "")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
            if not client_id or not client_secret:
                raise ToolException("Reddit credentials missing")
            auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
            data = {"grant_type": "client_credentials"}
            token = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers={"User-Agent": "ECHO/1.0"}, timeout=30).json()["access_token"]
            headers = {"Authorization": f"bearer {token}", "User-Agent": "ECHO/1.0"}
            r = requests.get(f"https://oauth.reddit.com/search?q={query}&limit={limit}", headers=headers, timeout=30)
            r.raise_for_status()
            children = r.json().get("data", {}).get("children", [])
            return "\n".join(f"- {c['data'].get('title')} ({c['data'].get('url')})" for c in children)
        if service == "youtube":
            key = os.getenv("YOUTUBE_API_KEY", "")
            if not key:
                raise ToolException("YOUTUBE_API_KEY missing")
            r = requests.get("https://www.googleapis.com/youtube/v3/search", params={"part": "snippet", "q": query, "maxResults": limit, "key": key}, timeout=30)
            r.raise_for_status()
            return "\n".join(f"- {it['snippet']['title']} (videoId={it['id'].get('videoId','')})" for it in r.json().get("items", []))
        return f"Unsupported service: {service}"
    except Exception as e:
        raise ToolException(str(e)) from e
