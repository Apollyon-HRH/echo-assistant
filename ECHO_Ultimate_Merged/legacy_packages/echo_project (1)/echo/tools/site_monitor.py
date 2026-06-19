"""Monitor a site by comparing content hashes."""

from __future__ import annotations
from pathlib import Path
import hashlib
import json
import time
import requests

from tools._common import ToolException, DATA_DIR, safe_json_load, safe_json_dump, now_iso

STATE = DATA_DIR / "site_monitor.json"

def site_monitor(url: str, mode: str = "check") -> str:
    """Check or register the current snapshot of a URL."""
    state = safe_json_load(STATE, {})
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        digest = hashlib.sha256(r.text.encode("utf-8", errors="ignore")).hexdigest()
    except Exception as e:
        raise ToolException(f"Falha ao monitorar site: {e}")
    item = state.get(url)
    if mode == "register" or item is None:
        state[url] = {"hash": digest, "last_seen": now_iso()}
        safe_json_dump(STATE, state)
        return f"Registrado: {url}"
    changed = item.get("hash") != digest
    state[url] = {"hash": digest, "last_seen": now_iso()}
    safe_json_dump(STATE, state)
    return f"{url} | changed={changed} | previous={item.get('hash')} | current={digest}"
