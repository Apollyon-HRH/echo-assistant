from __future__ import annotations

from pathlib import Path
import json

from tools._base import ToolException

CRON_FILE = Path("memory/cron_jobs.json")
CRON_FILE.parent.mkdir(exist_ok=True)

def cron(action: str, job_id: str | None = None, payload: str | None = None) -> str:
    """Persist cron-like jobs in JSON."""
    try:
        jobs = json.loads(CRON_FILE.read_text(encoding="utf-8")) if CRON_FILE.exists() else []
        if action == "list":
            return json.dumps(jobs, ensure_ascii=False, indent=2)
        if action == "add" and payload:
            jobs.append({"id": job_id or f"job_{len(jobs)+1}", "payload": payload})
            CRON_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
            return "added"
        if action == "remove" and job_id:
            jobs = [j for j in jobs if j.get("id") != job_id]
            CRON_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
            return "removed"
        raise ToolException("Unsupported cron action")
    except Exception as e:
        raise ToolException(str(e)) from e
