from core.exceptions import ToolException

def embeddings(text: str, model: str = "nomic-embed-text") -> str:
    """Generate embeddings using Ollama or SentenceTransformers."""
    try:
        import requests, json
        resp = requests.post("http://localhost:11434/api/embeddings", json={"model": model, "prompt": text}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return json.dumps(data.get("embedding", []), ensure_ascii=False)
    except Exception as e:
        try:
            from sentence_transformers import SentenceTransformer
            model_obj = SentenceTransformer(model)
            vec = model_obj.encode([text])[0].tolist()
            import json
            return json.dumps(vec, ensure_ascii=False)
        except Exception as inner:
            raise ToolException(f"Erro na ferramenta embeddings: {e}; fallback: {inner}") from inner
