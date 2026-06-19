"""Ollama model orchestration and routing for ECHO."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional
import json
import re
import time
import subprocess

import requests

from core.config import CONFIG
from tools._common import ToolException


CODE_KEYWORDS = [
    "código", "função", "script", "debug", "algoritmo", "parser", "compilador",
    "injetar", "exploit", "buffer", "overflow", "reverse", "engenharia reversa",
    "assembly", "ponteiro", "malloc", "fork", "thread", "socket", "payload", "shellcode",
]

GENERAL_DEEP_KEYWORDS = ["explique", "detalhe", "teoria", "história", "filosofia", "por que", "como funciona", "significado"]


def count_words(text: str) -> int:
    """Count words in a string."""
    return len(re.findall(r"\S+", text or ""))


def route_model_name(message: str, model_map: dict[str, str], forced: str | None = None) -> str:
    """Choose the model based on prompt content and manual overrides."""
    if forced and forced in model_map:
        return model_map[forced]
    low = (message or "").lower()
    words = count_words(low)
    if any(k in low for k in CODE_KEYWORDS):
        return model_map["codigo_pesado"] if words >= 10 else model_map["codigo_leve"]
    if any(k in low for k in GENERAL_DEEP_KEYWORDS):
        return model_map["geral_pesado"]
    if words > 30:
        return model_map["geral_pesado"]
    return model_map["geral_leve"]


class ModelManager:
    """Manage one Ollama model at a time with fallback and streaming."""

    def __init__(self, model_name: str, context_length: int = 8192, system_prompt: str | None = None, model_map: dict[str, str] | None = None):
        """Initialize the model manager."""
        self.model = model_name
        self.context_length = context_length
        self.system_prompt = system_prompt or CONFIG["system_prompt"]
        self.model_map = model_map or CONFIG["models"]
        self.session = requests.Session()

    def set_model(self, model_name: str) -> str:
        """Switch the active model."""
        self.model = model_name
        return self.model

    def _call_ollama(self, prompt: str, stream: bool = True):
        """Call the Ollama generate API."""
        payload = {
            "model": self.model,
            "prompt": f"{self.system_prompt}\n\n{prompt}",
            "stream": stream,
            "options": {"num_ctx": self.context_length},
        }
        try:
            resp = self.session.post("http://localhost:11434/api/generate", json=payload, stream=stream, timeout=CONFIG["timeouts"]["ollama_request"])
            if resp.status_code == 404:
                raise ToolException(f"Modelo não encontrado: {self.model}. Execute `ollama pull {self.model}`.")
            resp.raise_for_status()
            return resp
        except requests.exceptions.ConnectionError as e:
            raise ToolException("Ollama não está rodando. Execute 'ollama serve'.") from e
        except requests.RequestException as e:
            raise ToolException(f"Falha ao chamar Ollama: {e}") from e

    def ask_stream(self, prompt: str):
        """Yield streamed chunks from the model."""
        try:
            resp = self._call_ollama(prompt, stream=True)
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    if chunk:
                        yield chunk
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
        except ToolException:
            fallback = self.model_map["geral_leve"]
            if self.model != fallback:
                self.model = fallback
                yield from self.ask_stream(prompt)
            else:
                raise

    def ask_sync(self, prompt: str) -> str:
        """Return the complete model response."""
        try:
            resp = self._call_ollama(prompt, stream=False)
            data = resp.json()
            return data.get("response", "")
        except ToolException:
            fallback = self.model_map["geral_leve"]
            if self.model != fallback:
                self.model = fallback
                return self.ask_sync(prompt)
            raise

    def ask(self, prompt: str, stream: bool = True, tools: list[str] | None = None):
        """Ask the active model."""
        return self.ask_stream(prompt) if stream else self.ask_sync(prompt)

    def unload_current(self) -> None:
        """Attempt to unload the current model to save VRAM."""
        try:
            subprocess.run(["ollama", "stop", self.model], capture_output=True, text=True, timeout=20)
        except Exception:
            pass
