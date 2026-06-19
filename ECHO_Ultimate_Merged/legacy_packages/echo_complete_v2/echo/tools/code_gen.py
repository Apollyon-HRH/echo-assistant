from __future__ import annotations

import os
import requests

from tools._base import ToolException

def code_gen(description: str, lang: str = "python") -> str:
    """Generate code using the current Ollama code model."""
    try:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        model = os.getenv("ECHO_CODE_MODEL", "huihui_ai/qwen2.5-coder-abliterate:7b")
        prompt = f"Write clean, production-ready {lang} code for: {description}"
        r = requests.post(f"{host}/api/generate", json={"model": model, "prompt": prompt, "stream": False, "options": {"num_ctx": 8192}}, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "")
    except Exception as e:
        raise ToolException(str(e)) from e
