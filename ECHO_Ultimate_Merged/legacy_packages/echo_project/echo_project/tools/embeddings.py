"""Embeddings tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def embeddings(text: str, model: str = "", **kwargs) -> str:
    """Generate embeddings using Ollama or SentenceTransformers if available."""
    try:
        import requests
        if model:
            payload = {"model": model, "prompt": text}
            resp = requests.post("http://localhost:11434/api/embeddings", json=payload, timeout=60)
            if resp.status_code == 200:
                return json_dump(resp.json())
        try:
            from sentence_transformers import SentenceTransformer
            st = SentenceTransformer("all-MiniLM-L6-v2")
            vec = st.encode([text])[0].tolist()
            return json_dump(vec)
        except Exception as exc:
            raise ToolException(f"No embeddings backend available: {exc}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
