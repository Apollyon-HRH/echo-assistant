from __future__ import annotations

import math
import re
from collections import Counter

from core.exceptions import ToolException
from ._shared import json_pretty

def _vectorize(text: str, dims: int = 256):
    vec = [0.0] * dims
    for word in re.findall(r"\b\w+\b", text.lower()):
        idx = hash(word) % dims
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]

def embeddings(text: str, compare_to: str | None = None) -> str:
    """Generate lightweight hash embeddings and optional cosine similarity."""
    if not text.strip():
        raise ToolException("text cannot be empty")
    v1 = _vectorize(text)
    result = {"embedding": v1}
    if compare_to is not None:
        v2 = _vectorize(compare_to)
        sim = sum(a * b for a, b in zip(v1, v2))
        result["similarity"] = sim
    return json_pretty(result)
