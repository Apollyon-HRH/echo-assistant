from __future__ import annotations

import hashlib
from tools._shared import json_dump
from core.exceptions import ToolException

def embeddings(text: str, dimensions: int = 64, **kwargs) -> str:
    """Produce a deterministic pseudo-embedding for offline workflows."""
    try:
        vectors = []
        seed = text.encode("utf-8")
        for i in range(dimensions):
            digest = hashlib.sha256(seed + str(i).encode()).digest()
            vectors.append((int.from_bytes(digest[:2], "big") / 65535.0) * 2 - 1)
        return json_dump({"dimensions": dimensions, "vector": vectors})
    except Exception as exc:
        raise ToolException(f"embeddings failed: {exc}")
