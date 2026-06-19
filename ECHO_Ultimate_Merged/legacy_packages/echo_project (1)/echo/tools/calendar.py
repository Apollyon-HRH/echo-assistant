"""Local calendar/event registry."""

from __future__ import annotations
from pathlib import Path
import json

from tools._common import ToolException, DATA_DIR, safe_json_load, safe_json_dump, now_iso

STATE = DATA_DIR / "calendar_events.json"

def calendar(action: str, title: str | None = None, when: str | None = None, notes: str | None = None) -> str:
    """Manage simple local calendar entries."""
    data = safe_json_load(STATE, [])
    if action == "list":
        return json.dumps(data, ensure_ascii=False, indent=2)
    if action == "add":
        if not title or not when:
            raise ToolException("title e when são obrigatórios.")
        data.append({"title": title, "when": when, "notes": notes or "", "created": now_iso()})
        safe_json_dump(STATE, data)
        return f"Evento adicionado: {title}"
    if action == "remove":
        data = [x for x in data if x.get("title") != title]
        safe_json_dump(STATE, data)
        return f"Evento removido: {title}"
    raise ToolException(f"Ação inválida: {action}")
