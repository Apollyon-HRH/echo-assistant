"""Simple persistent task scheduler registry."""

from __future__ import annotations
from pathlib import Path
import json

from tools._common import ToolException, DATA_DIR, safe_json_load, safe_json_dump, now_iso

STATE = DATA_DIR / "cron_jobs.json"

def cron(action: str, name: str | None = None, schedule: str | None = None, command: str | None = None) -> str:
    """Manage simple cron-like jobs persisted locally."""
    state = safe_json_load(STATE, [])
    if action == "list":
        return json.dumps(state, ensure_ascii=False, indent=2)
    if action == "add":
        if not all([name, schedule, command]):
            raise ToolException("name, schedule e command são obrigatórios.")
        state.append({"name": name, "schedule": schedule, "command": command, "created": now_iso()})
        safe_json_dump(STATE, state)
        return f"Job adicionado: {name}"
    if action == "remove":
        if not name:
            raise ToolException("name é obrigatório.")
        state = [x for x in state if x.get("name") != name]
        safe_json_dump(STATE, state)
        return f"Job removido: {name}"
    raise ToolException(f"Ação inválida: {action}")
