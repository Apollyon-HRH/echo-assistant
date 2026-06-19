from __future__ import annotations

import re
from tools._shared import json_dump
from core.exceptions import ToolException

def ner(text: str, **kwargs) -> str:
    """Extract capitalized entities using a lightweight heuristic."""
    try:
        entities = re.findall(r"\b[A-ZÀ-Ý][\wÀ-ÿ\-]{2,}\b", text)
        return json_dump({"entities": list(dict.fromkeys(entities))})
    except Exception as exc:
        raise ToolException(f"ner failed: {exc}")
