from __future__ import annotations

import requests
from tools._shared import json_dump
from core.config import CONFIG
from core.exceptions import ToolException

def home_assistant(path: str, method: str = "GET", json_body=None, **kwargs) -> str:
    """Call the Home Assistant REST API."""
    try:
        base = CONFIG.get("env", {}).get("home_assistant_url", "").rstrip("/")
        token = CONFIG.get("env", {}).get("home_assistant_token", "")
        if not base or not token:
            raise ToolException("HOME_ASSISTANT_URL/TOKEN is not configured")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        r = requests.request(method.upper(), base + path, headers=headers, json=json_body, timeout=30)
        r.raise_for_status()
        try:
            payload = r.json()
        except Exception:
            payload = r.text
        return json_dump(payload)
    except Exception as exc:
        raise ToolException(f"home_assistant failed: {exc}")
