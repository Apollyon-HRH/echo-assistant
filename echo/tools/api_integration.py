from __future__ import annotations

import requests
from tools._shared import json_dump
from core.exceptions import ToolException

def api_integration(url: str, method: str = "GET", json_body=None, headers=None, timeout: int = 30, **kwargs) -> str:
    """Call a REST API endpoint and return structured output."""
    try:
        method = method.upper()
        headers = headers or {}
        r = requests.request(method, url, json=json_body, headers=headers, timeout=timeout)
        payload = None
        try:
            payload = r.json()
        except Exception:
            payload = r.text[:12000]
        return json_dump({"status_code": r.status_code, "ok": r.ok, "payload": payload})
    except Exception as exc:
        raise ToolException(f"api_integration failed: {exc}")
