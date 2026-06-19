"""Cron registration tool."""

from __future__ import annotations

import json
from pathlib import Path

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def cron(spec: str, command: str, **kwargs) -> str:
    """Register a cron-like schedule in a local JSON file."""
    try:
        from pathlib import Path
        import json
        store = Path("memory") / "cron_jobs.json"
        store.parent.mkdir(parents=True, exist_ok=True)
        jobs = []
        if store.exists():
            jobs = json.loads(store.read_text(encoding="utf-8"))
        job = {"spec": spec, "command": command, "created_at": now_iso()}
        jobs.append(job)
        store.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
        return json_dump(job)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
