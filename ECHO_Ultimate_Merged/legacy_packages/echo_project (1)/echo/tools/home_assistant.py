"""Home Assistant REST helper."""

from __future__ import annotations
import os
import requests

from tools._common import ToolException

def home_assistant(action: str, entity_id: str | None = None, service: str | None = None, payload: str | None = None) -> str:
    """Call Home Assistant REST endpoints."""
    base = os.getenv("HOME_ASSISTANT_URL", "").rstrip("/")
    token = os.getenv("HOME_ASSISTANT_TOKEN", "")
    if not base or not token:
        raise ToolException("Home Assistant não configurado.")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        if action == "state":
            r = requests.get(f"{base}/api/states/{entity_id}", headers=headers, timeout=30)
            r.raise_for_status()
            return r.text
        if action == "call":
            if not service or not entity_id:
                raise ToolException("service e entity_id são obrigatórios.")
            domain, srv = service.split(".", 1)
            body = {"entity_id": entity_id}
            if payload:
                import json
                body.update(json.loads(payload))
            r = requests.post(f"{base}/api/services/{domain}/{srv}", headers=headers, json=body, timeout=30)
            r.raise_for_status()
            return r.text
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Falha no Home Assistant: {e}")
