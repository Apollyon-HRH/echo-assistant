"""Generic HTTP API client."""

from __future__ import annotations
import json
import requests

from tools._common import ToolException, clamp_text


def api_integration(url: str, method: str = "GET", headers: str | None = None, data: str | None = None, timeout: int = 30) -> str:
    """Call an arbitrary API endpoint."""
    try:
        hdrs = json.loads(headers) if headers else {}
        payload = json.loads(data) if data else None
    except Exception as e:
        raise ToolException(f"Headers/data inválidos: {e}")

    try:
        r = requests.request(method.upper(), url, headers=hdrs, json=payload, timeout=timeout)
        return clamp_text(f"STATUS {r.status_code}\n{r.text}", 12000)
    except Exception as e:
        raise ToolException(f"Falha na integração API: {e}")
