from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from core.config import CONFIG
from core.exceptions import ToolException
from ._shared import TEMP_DIR, json_pretty

CAL_FILE = Path(CONFIG["runtime"]["root"]) / "memory" / "calendar.json"

def calendar(action: str, title: str = "", when: str = "", description: str = "") -> str:
    """Store and list local calendar events in JSON."""
    action = action.lower().strip()
    events = []
    if CAL_FILE.exists():
        try:
            events = json.loads(CAL_FILE.read_text(encoding="utf-8"))
        except Exception:
            events = []

    if action == "add":
        if not title or not when:
            raise ToolException("title and when are required")
        events.append({"title": title, "when": when, "description": description})
        CAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        CAL_FILE.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
        return "Event added"

    if action == "list":
        return json_pretty(events)

    if action == "clear":
        events = []
        CAL_FILE.write_text("[]", encoding="utf-8")
        return "Calendar cleared"

    raise ToolException(f"Unsupported action: {action}")
