
"""Ollama model orchestration for ECHO."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Generator, Iterable, List, Optional

import requests

from .config import CONFIG
from .exceptions import OllamaError

OLLAMA_URL = "http://localhost:11434/api/generate"


@dataclass
class ModelResult:
    """Container for model responses."""
    text: str
    model: str
    elapsed: float


class ModelManager:
    """Manage a single active Ollama model with fallback and streaming."""

    def __init__(self, model_name: str, context_length: int = 8192, system_prompt: Optional[str] = None) -> None:
        """Create a model manager."""
        self.model = model_name
        self.context_length = context_length
        self.system_prompt = system_prompt or CONFIG["system_prompt"]
        self.last_error: Optional[str] = None

    def set_model(self, model_name: str) -> None:
        """Switch to a different model name."""
        self.model = model_name

    def _call_ollama(self, prompt: str, stream: bool) -> requests.Response:
        """Send a request to Ollama's generate endpoint."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {"num_ctx": self.context_length},
        }
        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=CONFIG["timeouts"]["ollama_request"],
                stream=stream,
            )
            response.raise_for_status()
            return response
        except Exception as exc:
            self.last_error = str(exc)
            raise OllamaError(f"Ollama request failed: {exc}") from exc

    def _build_prompt(self, prompt: str) -> str:
        """Prepend the system prompt to the user prompt."""
        return f"{self.system_prompt}\n\nUser: {prompt}\n\nAssistant:"

    def ask_stream(self, prompt: str) -> Generator[str, None, None]:
        """Yield streaming tokens from the model."""
        response = self._call_ollama(self._build_prompt(prompt), stream=True)
        for raw in response.iter_lines(decode_unicode=True):
            if not raw:
                continue
            try:
                data = json.loads(raw)
                chunk = data.get("response", "")
                if chunk:
                    yield chunk
                if data.get("done"):
                    break
            except json.JSONDecodeError:
                continue

    def ask_sync(self, prompt: str) -> str:
        """Return the full response as a string."""
        response = self._call_ollama(self._build_prompt(prompt), stream=False)
        try:
            data = response.json()
            return data.get("response", "")
        except Exception as exc:
            raise OllamaError(f"Invalid Ollama response: {exc}") from exc

    def ask(self, prompt: str, stream: bool = True, tools: Optional[List[str]] = None):
        """Ask the model with optional streaming."""
        try:
            if stream:
                return self.ask_stream(prompt)
            return self.ask_sync(prompt)
        except OllamaError:
            fallback = CONFIG["models"]["geral_leve"]
            if self.model != fallback:
                old = self.model
                self.model = fallback
                try:
                    return self.ask(prompt, stream=stream, tools=tools)
                finally:
                    self.model = old
            raise

    def token_estimate(self, messages: Iterable[Dict[str, str]]) -> int:
        """Estimate the token count from message contents."""
        chars = sum(len(m.get("content", "")) for m in messages)
        return max(1, chars // 4)
