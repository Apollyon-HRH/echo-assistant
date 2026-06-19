from __future__ import annotations

import os
import requests

from tools._base import ToolException

def home_assistant(path: str = "/api/states", method: str = "GET", payload: dict | None = None) -> str:
    """Interact with Home Assistant REST API."""
    try:
        base = os.getenv("HOME_ASSISTANT_URL", "").rstrip("/")
        token = os.getenv("HOME_ASSISTANT_TOKEN", "")
        if not base or not token:
            raise ToolException("Home Assistant env vars missing")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = base + path
        r = requests.request(method.upper(), url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.text[:4000]
    except Exception as e:
        raise ToolException(str(e)) from e
