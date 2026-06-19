from __future__ import annotations
from pathlib import Path
import hashlib

def hash_file(path: str, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
