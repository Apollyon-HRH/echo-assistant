"""Timer registration tool."""

from __future__ import annotations

import json
from pathlib import Path

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def timer(seconds: int, message: str = "Timer completed", **kwargs) -> str:
    """Create a delay marker for later processing."""
    try:
        from pathlib import Path
        import json
        store = Path("memory") / "timers.json"
        store.parent.mkdir(parents=True, exist_ok=True)
        timers = []
        if store.exists():
            timers = json.loads(store.read_text(encoding="utf-8"))
        timer_item = {"seconds": seconds, "message": message, "created_at": now_iso()}
        timers.append(timer_item)
        store.write_text(json.dumps(timers, ensure_ascii=False, indent=2), encoding="utf-8")
        return json_dump(timer_item)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
