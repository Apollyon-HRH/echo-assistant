from __future__ import annotations

from tools._shared import json_dump
from core.exceptions import ToolException

def toast(title: str, message: str, **kwargs) -> str:
    """Show a desktop notification when supported."""
    try:
        try:
            from plyer import notification
            notification.notify(title=title, message=message, app_name="ECHO")
            return json_dump({"shown": True})
        except Exception:
            return json_dump({"title": title, "message": message, "fallback": True})
    except Exception as exc:
        raise ToolException(f"toast failed: {exc}")
