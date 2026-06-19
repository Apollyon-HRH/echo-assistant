from __future__ import annotations

import secrets
import string
from tools._shared import json_dump
from core.exceptions import ToolException

def password(length: int = 24, symbols: bool = True, **kwargs) -> str:
    """Generate a strong password."""
    try:
        alphabet = string.ascii_letters + string.digits + (string.punctuation if symbols else "")
        result = "".join(secrets.choice(alphabet) for _ in range(length))
        return json_dump({"password": result})
    except Exception as exc:
        raise ToolException(f"password failed: {exc}")
