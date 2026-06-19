from __future__ import annotations

import json
from pathlib import Path

import requests

from core.exceptions import ToolException
from ._shared import TEMP_DIR, sha256_text, ensure_parent, json_pretty

STATE_FILE = TEMP_DIR / "site_monitor_state.json"

def site_monitor(url: str, state_key: str | None = None, timeout: int = 30) -> str:
    """Monitor a site by hashing its current content and comparing against local state."""
    if not url.strip():
        raise ToolException("url cannot be empty")
    key = state_key or url
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        content = r.text
    except Exception as exc:
        raise ToolException(f"Failed to fetch site: {exc}") from exc

    current_hash = sha256_text(content)
    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    previous = state.get(key)
    state[key] = current_hash
    ensure_parent(STATE_FILE)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    changed = previous is not None and previous != current_hash
    return json_pretty({"url": url, "changed": changed, "hash": current_hash, "previous": previous})
