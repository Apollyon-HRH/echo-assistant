from __future__ import annotations

import hashlib
from pathlib import Path

from core.exceptions import ToolException
from ._shared import sha256_file, md5_file

def hash(path: str, algorithm: str = "sha256") -> str:
    """Compute a checksum for a file."""
    p = Path(path).expanduser()
    if not p.exists():
        raise ToolException(f"Path not found: {p}")
    algorithm = algorithm.lower().strip()
    if algorithm == "sha256":
        return sha256_file(p)
    if algorithm == "md5":
        return md5_file(p)
    h = hashlib.new(algorithm)
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
