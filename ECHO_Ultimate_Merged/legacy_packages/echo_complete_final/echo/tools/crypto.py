from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from core.exceptions import ToolException
from ._shared import json_pretty

def crypto(action: str, text: str = "", key: str = "", algorithm: str = "sha256") -> str:
    """Provide hashing, HMAC, and secure random generation."""
    action = action.lower().strip()
    if action == "hash":
        h = hashlib.new(algorithm)
        h.update(text.encode("utf-8"))
        return h.hexdigest()
    if action == "hmac":
        if not key:
            raise ToolException("key is required for HMAC")
        return hmac.new(key.encode("utf-8"), text.encode("utf-8"), algorithm).hexdigest()
    if action == "random":
        return secrets.token_urlsafe(32)
    if action == "base64":
        return base64.b64encode(text.encode("utf-8")).decode("ascii")
    if action == "unbase64":
        return base64.b64decode(text.encode("ascii")).decode("utf-8", errors="replace")
    raise ToolException(f"Unsupported action: {action}")
