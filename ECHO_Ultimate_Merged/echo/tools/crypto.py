from __future__ import annotations

import base64
from tools._shared import json_dump
from core.exceptions import ToolException

def crypto(action: str, text: str, **kwargs) -> str:
    """Small crypto helpers like base64 encode/decode."""
    try:
        if action == "b64encode":
            return json_dump({"result": base64.b64encode(text.encode()).decode()})
        if action == "b64decode":
            return json_dump({"result": base64.b64decode(text.encode()).decode(errors="replace")})
        raise ToolException(f"Unknown action: {action}")
    except Exception as exc:
        raise ToolException(f"crypto failed: {exc}")
