from __future__ import annotations

import re

from core.exceptions import ToolException
from ._shared import json_pretty

def classifier(text: str, labels: str = "question,command,information,code") -> str:
    """Simple rule-based text classifier."""
    text = text.strip()
    if not text:
        raise ToolException("text cannot be empty")
    labels_list = [x.strip() for x in labels.split(",") if x.strip()]
    lower = text.lower()
    if lower.endswith("?"):
        pred = "question"
    elif any(k in lower for k in ["run", "execute", "open", "delete", "create"]):
        pred = "command"
    elif any(k in lower for k in ["code", "function", "script", "class", "def "]):
        pred = "code"
    else:
        pred = "information"
    if pred not in labels_list:
        pred = labels_list[0] if labels_list else pred
    return json_pretty({"label": pred, "labels": labels_list})
