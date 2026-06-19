"""API integration tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def api_integration(service: str, query: str = "", **kwargs) -> str:
    """Access common web APIs such as GitHub, Reddit, Twitter and YouTube."""
    try:
        import os
        import requests
        service = service.lower().strip()
        if service == "github":
            token = os.getenv("GITHUB_TOKEN", "")
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            url = f"https://api.github.com/search/repositories?q={requests.utils.quote(query)}"
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            return json_dump(resp.json().get("items", [])[:5])
        if service == "reddit":
            client_id = os.getenv("REDDIT_CLIENT_ID", "")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
            if client_id and client_secret:
                return json_dump({"note": "Reddit API credentials present; implement OAuth flow as needed."})
            url = f"https://www.reddit.com/search.json?q={requests.utils.quote(query)}&limit=5"
            resp = requests.get(url, headers={"User-Agent": "ECHO/1.0"}, timeout=30)
            resp.raise_for_status()
            return json_dump(resp.json())
        if service == "youtube":
            key = os.getenv("YOUTUBE_API_KEY", "")
            if not key:
                raise ToolException("YOUTUBE_API_KEY missing")
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={requests.utils.quote(query)}&key={key}&maxResults=5&type=video"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            return json_dump(resp.json())
        if service == "twitter":
            token = os.getenv("TWITTER_BEARER_TOKEN", "")
            if not token:
                raise ToolException("TWITTER_BEARER_TOKEN missing")
            url = f"https://api.twitter.com/2/tweets/search/recent?query={requests.utils.quote(query)}"
            resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
            resp.raise_for_status()
            return json_dump(resp.json())
        raise ToolException(f"Unsupported service: {service}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
