from __future__ import annotations

import hashlib
from pathlib import Path

from tools._base import ToolException

def hash(path: str, algorithm: str = "sha256") -> str:
    """Compute file hash."""
    try:
        p = Path(path)
        h = hashlib.new(algorithm)
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        raise ToolException(str(e)) from e
