"""Ollama model manager for ECHO."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Dict, Generator, Iterable, Optional

import requests

from core.config import CONFIG
from core.exceptions import ModelException
from core.logger import setup_logger

logger = setup_logger("ECHO.Model")


@dataclass
class OllamaResponse:
    """Container for model responses."""
    text: str
    elapsed: float
    model: str


class ModelManager:
    """Manage one Ollama model at a time, with streaming and fallback."""

    def __init__(self, model_name: str, context_length: int = 8192, system_prompt: str | None = None) -> None:
        self.model = model_name
        self.context_length = context_length
        self.system_prompt = system_prompt or CONFIG.get("system_prompt", "")
        self.base_url = CONFIG.get("ollama", {}).get("base_url", "http://localhost:11434")

    def set_model(self, model_name: str) -> None:
        """Switch the active model."""
        self.model = model_name

    def _build_prompt(self, prompt: str) -> str:
        """Apply the system prompt to the user prompt."""
        if self.system_prompt:
            return f"{self.system_prompt}\n\nUser: {prompt}\nAssistant:"
        return prompt

    def _call_ollama(self, prompt: str, stream: bool = True, model: str | None = None):
        """Call Ollama generate endpoint."""
        payload = {
            "model": model or self.model,
            "prompt": self._build_prompt(prompt),
            "stream": stream,
            "options": {"num_ctx": self.context_length},
        }
        url = f"{self.base_url.rstrip('/')}/api/generate"
        try:
            return requests.post(url, json=payload, stream=stream, timeout=CONFIG["timeouts"]["ollama_request"])
        except requests.RequestException as exc:
            raise ModelException("Ollama não está rodando. Execute 'ollama serve'.") from exc

    def ask_stream(self, prompt: str) -> Generator[str, None, None]:
        """Yield text chunks from the active model."""
        response = self._call_ollama(prompt, stream=True)
        if response.status_code != 200:
            raise ModelException(f"Erro no Ollama: HTTP {response.status_code}")
        try:
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                data = json.loads(raw_line)
                chunk = data.get("response", "")
                if chunk:
                    yield chunk
                if data.get("done"):
                    break
        finally:
            response.close()

    def ask_sync(self, prompt: str) -> str:
        """Return the full response from the active model, with fallback."""
        start = time.time()
        try:
            response = self._call_ollama(prompt, stream=False)
            if response.status_code != 200:
                raise ModelException(f"Erro no Ollama: HTTP {response.status_code}")
            data = response.json()
            text = data.get("response", "")
            return text
        except ModelException:
            logger.error("Ollama offline or unavailable")
            raise
        except Exception as exc:
            logger.warning("Primary model failed; attempting fallback: %s", exc)
            fallback = CONFIG.get("models", {}).get("geral_leve")
            if fallback and fallback != self.model:
                response = self._call_ollama(prompt, stream=False, model=fallback)
                if response.status_code != 200:
                    raise ModelException(f"Erro no Ollama fallback: HTTP {response.status_code}")
                return response.json().get("response", "")
            raise ModelException(str(exc)) from exc

    def ask(self, prompt: str, stream: bool = True, tools=None):
        """Ask the model using either streaming or synchronous mode."""
        if stream:
            return self.ask_stream(prompt)
        return self.ask_sync(prompt)
