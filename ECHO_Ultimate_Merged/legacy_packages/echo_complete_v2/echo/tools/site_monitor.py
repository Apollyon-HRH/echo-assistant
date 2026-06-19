from __future__ import annotations

import json
from pathlib import Path

from tools._base import ToolException
from tools.common import http_get, json_dumps
from tools._utils import sha256_bytes, ensure_parent

STATE_FILE = Path("memory/site_monitor.json")
STATE_FILE.parent.mkdir(exist_ok=True)

def site_monitor(url: str) -> str:
    """Store and compare content hash of a site."""
    try:
        resp = http_get(url, timeout=60)
        content = resp.text.encode("utf-8", errors="ignore")
        current = sha256_bytes(content)
        old = None
        if STATE_FILE.exists():
            old = json.loads(STATE_FILE.read_text(encoding="utf-8")).get(url)
        STATE_FILE.write_text(json.dumps({**({} if not STATE_FILE.exists() else json.loads(STATE_FILE.read_text(encoding="utf-8"))), url: current}, indent=2), encoding="utf-8")
        return f"hash={current}" + (f" changed={old != current}" if old else "")
    except Exception as e:
        raise ToolException(str(e)) from e
