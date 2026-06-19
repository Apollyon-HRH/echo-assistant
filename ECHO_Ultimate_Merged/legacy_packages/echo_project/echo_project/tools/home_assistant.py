"""Home Assistant integration tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def home_assistant(entity_id: str, action: str = "status", **kwargs) -> str:
    """Interact with Home Assistant REST API."""
    try:
        import os
        import requests
        base_url = os.getenv("HOME_ASSISTANT_URL", "")
        token = os.getenv("HOME_ASSISTANT_TOKEN", "")
        if not base_url or not token:
            raise ToolException("Home Assistant configuration missing")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        if action == "status":
            resp = requests.get(f"{base_url}/api/states/{entity_id}", headers=headers, timeout=30)
        else:
            domain = entity_id.split(".", 1)[0]
            service = action
            resp = requests.post(f"{base_url}/api/services/{domain}/{service}", headers=headers, json={"entity_id": entity_id}, timeout=30)
        resp.raise_for_status()
        return json_dump(resp.json())
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
