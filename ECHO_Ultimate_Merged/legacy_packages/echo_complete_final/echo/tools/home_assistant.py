from __future__ import annotations

import requests

from core.config import CONFIG
from core.exceptions import ToolException
from ._shared import json_pretty

def home_assistant(action: str, domain: str = "", service: str = "", entity_id: str = "", data: dict | None = None) -> str:
    """Call Home Assistant REST API services or states."""
    env = CONFIG.get("env", {})
    url = env.get("home_assistant_url")
    token = env.get("home_assistant_token")
    if not url or not token:
        raise ToolException("Home Assistant configuration missing")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        if action == "call_service":
            if not domain or not service:
                raise ToolException("domain and service required")
            payload = data or {}
            if entity_id:
                payload.setdefault("entity_id", entity_id)
            r = requests.post(f"{url.rstrip('/')}/api/services/{domain}/{service}", json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            return json_pretty(r.json())
        if action == "state":
            if not entity_id:
                raise ToolException("entity_id required")
            r = requests.get(f"{url.rstrip('/')}/api/states/{entity_id}", headers=headers, timeout=30)
            r.raise_for_status()
            return json_pretty(r.json())
        raise ToolException(f"Unsupported action: {action}")
    except Exception as exc:
        raise ToolException(f"home_assistant failed: {exc}") from exc
