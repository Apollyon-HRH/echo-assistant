from __future__ import annotations

from urllib.parse import urlencode

import requests

from core.config import CONFIG
from core.exceptions import ToolException
from ._shared import json_pretty

def api_integration(service: str, query: str = "", endpoint: str = "", method: str = "GET", data: dict | None = None) -> str:
    """Generic integration helper for public APIs and webhooks."""
    service = service.lower().strip()
    env = CONFIG.get("env", {})
    headers = {"User-Agent": "ECHO/1.0"}

    try:
        if service == "github":
            token = env.get("github_token")
            if not token:
                raise ToolException("GITHUB_TOKEN not configured")
            headers["Authorization"] = f"Bearer {token}"
            url = endpoint or f"https://api.github.com{query}"
            r = requests.request(method, url, headers=headers, json=data, timeout=30)
            r.raise_for_status()
            return json_pretty(r.json())

        if service == "reddit":
            client_id = env.get("reddit_client_id")
            client_secret = env.get("reddit_client_secret")
            if not client_id or not client_secret:
                raise ToolException("Reddit credentials not configured")
            auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
            token_res = requests.post("https://www.reddit.com/api/v1/access_token",
                                      auth=auth,
                                      data={"grant_type": "client_credentials"},
                                      headers={"User-Agent": "ECHO/1.0"},
                                      timeout=30)
            token_res.raise_for_status()
            access_token = token_res.json()["access_token"]
            headers["Authorization"] = f"bearer {access_token}"
            url = endpoint or f"https://oauth.reddit.com{query}"
            r = requests.request(method, url, headers=headers, json=data, timeout=30)
            r.raise_for_status()
            return json_pretty(r.json())

        if service == "youtube":
            api_key = env.get("youtube_api_key")
            if not api_key:
                raise ToolException("YOUTUBE_API_KEY not configured")
            url = endpoint or f"https://www.googleapis.com/youtube/v3/search?{urlencode({'part':'snippet','q':query,'key':api_key})}"
            r = requests.request(method, url, headers=headers, timeout=30)
            r.raise_for_status()
            return json_pretty(r.json())

        if service == "twitter":
            bearer = env.get("twitter_bearer_token")
            if not bearer:
                raise ToolException("TWITTER_BEARER_TOKEN not configured")
            headers["Authorization"] = f"Bearer {bearer}"
            url = endpoint or query
            r = requests.request(method, url, headers=headers, json=data, timeout=30)
            r.raise_for_status()
            return json_pretty(r.json())

        if service == "openweather":
            api_key = env.get("openweather_api_key")
            if not api_key:
                raise ToolException("OPENWEATHER_API_KEY not configured")
            url = endpoint or f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={api_key}&units=metric&lang=pt_br"
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            return json_pretty(r.json())

        raise ToolException(f"Unsupported service: {service}")
    except Exception as exc:
        raise ToolException(f"api_integration failed: {exc}") from exc
