from __future__ import annotations

from tools._base import ToolException

def classifier(text: str) -> str:
    """Rule-based text classifier."""
    try:
        lower = text.lower()
        if any(k in lower for k in ["bug", "error", "stack trace", "exception"]):
            return "software"
        if any(k in lower for k in ["invoice", "payment", "bank", "card"]):
            return "finance"
        if any(k in lower for k in ["meeting", "schedule", "calendar"]):
            return "productivity"
        return "general"
    except Exception as e:
        raise ToolException(str(e)) from e
