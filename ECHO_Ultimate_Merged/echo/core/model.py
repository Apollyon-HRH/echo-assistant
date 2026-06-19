
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Generator

import requests

from .config import CONFIG
from .exceptions import ModelException
from .logger import setup_logger

logger = setup_logger("echo.model")

@dataclass
class ModelReply:
    text: str
    model: str
    elapsed: float
    tokens_estimate: int = 0

class ModelManager:
    """Ollama client with streaming support."""

    def __init__(self, model_name: str, context_length: int = 8192, system_prompt: str | None = None) -> None:
        self.model = model_name
        self.context_length = context_length
        self.system_prompt = system_prompt or CONFIG.get("system_prompt", "")
        self.base_url = CONFIG.get("env", {}).get("ollama_base_url", "http://localhost:11434").rstrip("/")

    def set_model(self, model_name: str) -> None:
        self.model = model_name

    def _build_prompt(self, prompt: str) -> str:
        if self.system_prompt:
            return f"{self.system_prompt}\n\nUsuário: {prompt}\nAssistente:"
        return prompt

    def _call(self, prompt: str, stream: bool = True, model: str | None = None):
        payload = {
            "model": model or self.model,
            "prompt": self._build_prompt(prompt),
            "stream": stream,
            "options": {"num_ctx": self.context_length},
        }
        url = f"{self.base_url}/api/generate"
        try:
            return requests.post(url, json=payload, stream=stream, timeout=CONFIG["timeouts"]["ollama_request"])
        except requests.RequestException as exc:
            raise ModelException("Ollama indisponível. Verifique se 'ollama serve' está executando.") from exc

    def ask_stream(self, prompt: str) -> Generator[str, None, None]:
        response = self._call(prompt, stream=True)
        if response.status_code != 200:
            raise ModelException(f"Erro no Ollama: HTTP {response.status_code}")
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            try:
                data = json.loads(raw_line)
                chunk = data.get("response", "")
                if chunk:
                    yield chunk
                if data.get("done"):
                    break
            except json.JSONDecodeError:
                continue

    def ask(self, prompt: str) -> ModelReply:
        start = time.time()
        response = self._call(prompt, stream=False)
        if response.status_code != 200:
            raise ModelException(f"Erro no Ollama: HTTP {response.status_code}")
        data = response.json()
        text = data.get("response", "")
        elapsed = time.time() - start
        tokens_estimate = max(1, len(text) // 4)
        return ModelReply(text=text, model=data.get("model", self.model), elapsed=elapsed, tokens_estimate=tokens_estimate)
