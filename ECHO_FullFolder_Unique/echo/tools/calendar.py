from __future__ import annotations

import json
from pathlib import Path
from tools._shared import json_dump
from core.exceptions import ToolException

def calendar(action: str, event: str | None = None, store: str = "./memory/calendar.json", **kwargs) -> str:
    """Store lightweight calendar events."""
    try:
        path = Path(store)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        if action == "list":
            return json_dump(data)
        if action == "add":
            if not event:
                raise ToolException("event is required")
            data.append({"event": event})
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return json_dump({"added": event})
        if action == "clear":
            path.write_text("[]", encoding="utf-8")
            return json_dump({"cleared": True})
        raise ToolException(f"Unknown action: {action}")
    except Exception as exc:
        raise ToolException(f"calendar failed: {exc}")
