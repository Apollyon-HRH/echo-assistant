"""Hashing utilities."""

from __future__ import annotations
from pathlib import Path
import hashlib

from tools._common import ToolException

def hash(path_or_text: str, algorithm: str = "sha256", is_file: bool = False) -> str:
    """Compute a hash from a file or text."""
    try:
        h = hashlib.new(algorithm)
        if is_file:
            h.update(Path(path_or_text).read_bytes())
        else:
            h.update(path_or_text.encode("utf-8"))
        return h.hexdigest()
    except Exception as e:
        raise ToolException(f"Falha no hash: {e}")
