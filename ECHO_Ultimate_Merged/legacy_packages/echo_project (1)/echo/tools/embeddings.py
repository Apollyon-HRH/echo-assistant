"""Text embedding helper."""

from __future__ import annotations
import json
import math

from tools._common import ToolException

def embeddings(text: str, model: str = "all-MiniLM-L6-v2") -> str:
    """Compute embeddings using sentence-transformers when available."""
    try:
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer(model)
        vec = m.encode([text])[0].tolist()
        return json.dumps(vec)
    except Exception:
        # deterministic fallback vector
        tokens = [ord(c) % 997 for c in text[:256]]
        vec = [sum(tokens[i::8]) / max(1, len(tokens[i::8])) for i in range(8)]
        return json.dumps(vec)
