from __future__ import annotations

from tools._base import ToolException

def calendar(action: str = "list", title: str = "", date: str = "") -> str:
    """Calendar integration stub with real local file persistence fallback."""
    try:
        import json
        from pathlib import Path
        store = Path("memory/calendar_events.json")
        events = json.loads(store.read_text(encoding="utf-8")) if store.exists() else []
        if action == "list":
            return json.dumps(events, ensure_ascii=False, indent=2)
        if action == "add":
            events.append({"title": title, "date": date})
            store.parent.mkdir(exist_ok=True)
            store.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
            return "added"
        return "Unsupported action"
    except Exception as e:
        raise ToolException(str(e)) from e
