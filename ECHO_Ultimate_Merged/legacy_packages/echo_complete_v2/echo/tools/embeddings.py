from __future__ import annotations

from tools._base import ToolException

def embeddings(text: str, model: str = "all-MiniLM-L6-v2") -> str:
    """Generate embeddings using sentence-transformers or Ollama if available."""
    try:
        try:
            from sentence_transformers import SentenceTransformer
            model_obj = SentenceTransformer(model)
            vec = model_obj.encode([text])[0]
            return ",".join(f"{x:.6f}" for x in vec[:32])
        except Exception:
            import requests, os
            host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
            r = requests.post(f"{host}/api/embeddings", json={"model": model, "prompt": text}, timeout=120)
            r.raise_for_status()
            return str(r.json().get("embedding", []))
    except Exception as e:
        raise ToolException(str(e)) from e
