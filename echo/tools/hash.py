from __future__ import annotations

import hashlib
from tools._shared import json_dump
from core.exceptions import ToolException

def hash(text: str, algorithm: str = "sha256", **kwargs) -> str:
    """Hash text using a standard digest algorithm."""
    try:
        h = hashlib.new(algorithm)
        h.update(text.encode("utf-8"))
        return json_dump({"algorithm": algorithm, "digest": h.hexdigest()})
    except Exception as exc:
        raise ToolException(f"hash failed: {exc}")
