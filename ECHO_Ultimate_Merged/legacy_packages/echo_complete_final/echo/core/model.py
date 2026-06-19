from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, Generator, Iterable, List, Optional

import requests

from .config import CONFIG
from .exceptions import ModelError
from .logger import setup_logger

logger = setup_logger("echo.model")

KEYWORDS_CODE = (
    "código", "função", "script", "debug", "algoritmo", "parser", "compilador",
    "injetar", "exploit", "buffer", "overflow", "reverse", "engenharia reversa",
    "assembly", "ponteiro", "malloc", "fork", "thread", "socket", "payload", "shellcode"
)

KEYWORDS_GENERAL = ("explique", "detalhe", "teoria", "história", "filosofia", "por que", "como funciona", "significado")

class ModelManager:
    """Manage a single Ollama model at a time, with fallback and selection rules."""

    def __init__(self, model_name: str, context_length: int = 8192, system_prompt: str | None = None):
        self.models = CONFIG.get("models", {})
        self.context_length = int(context_length)
        self.system_prompt = system_prompt or CONFIG.get("system_prompt", "")
        self.current_model = model_name
        self.manual_mode = "auto"
        self.base_url = CONFIG.get("ollama", {}).get("base_url", "http://localhost:11434")
        self.session = requests.Session()
        self.timeout = int(CONFIG.get("ollama", {}).get("timeout", 120))

    def _stop_model(self, model_name: str) -> None:
        try:
            subprocess.run(["ollama", "stop", model_name], capture_output=True, text=True, timeout=15)
        except Exception:
            pass

    def set_model(self, model_name: str) -> str:
        """Unload current model and switch to a new one."""
        if model_name != self.current_model:
            self._stop_model(self.current_model)
            self.current_model = model_name
        return self.current_model

    def set_mode(self, mode: str) -> str:
        mode = mode.lower().strip()
        if mode not in {"auto", "gp", "gl", "cp", "cl"}:
            raise ModelError(f"Unknown mode: {mode}")
        self.manual_mode = mode
        return mode

    def choose_model(self, prompt: str) -> str:
        """Apply the exact switching rules from the prompt."""
        lower = prompt.lower().strip()
        word_count = len(re.findall(r"\S+", lower))

        if self.manual_mode != "auto":
            mapping = {
                "gp": self.models["geral_pesado"],
                "gl": self.models["geral_leve"],
                "cp": self.models["codigo_pesado"],
                "cl": self.models["codigo_leve"],
            }
            return mapping[self.manual_mode]

        if any(k in lower for k in KEYWORDS_CODE):
            return self.models["codigo_leve"] if word_count < 10 else self.models["codigo_pesado"]

        if any(k in lower for k in KEYWORDS_GENERAL):
            return self.models["geral_pesado"]

        if word_count > 30:
            return self.models["geral_pesado"]

        return self.models["geral_leve"]

    def _ollama_available(self) -> bool:
        try:
            r = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            return r.ok
        except Exception:
            return False

    def _call_ollama(self, prompt: str, stream: bool = True, model: str | None = None) -> Generator[str, None, str] | str:
        model = model or self.current_model
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {"num_ctx": self.context_length},
            "system": self.system_prompt,
        }

        try:
            response = self.session.post(f"{self.base_url}/api/generate", json=payload, stream=stream, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ModelError("Ollama não está rodando. Execute 'ollama serve'.") from exc

        if stream:
            def generator():
                buffer = []
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    chunk = obj.get("response", "")
                    if chunk:
                        buffer.append(chunk)
                        yield chunk
                    if obj.get("done"):
                        break
            return generator()

        data = response.json()
        return data.get("response", "")

    def ask_stream(self, prompt: str) -> Generator[str, None, None]:
        """Yield response chunks from Ollama with fallback."""
        model = self.choose_model(prompt)
        self.set_model(model)
        try:
            gen = self._call_ollama(prompt, stream=True, model=model)
            assert not isinstance(gen, str)
            yield from gen
        except ModelError as exc:
            logger.warning("Primary model failed (%s); falling back to general light model.", exc)
            fallback = self.models["geral_leve"]
            if fallback != model:
                self.set_model(fallback)
                gen = self._call_ollama(prompt, stream=True, model=fallback)
                assert not isinstance(gen, str)
                yield from gen
            else:
                raise

    def ask_sync(self, prompt: str) -> str:
        """Return the full model response as text."""
        model = self.choose_model(prompt)
        self.set_model(model)
        try:
            result = self._call_ollama(prompt, stream=False, model=model)
            assert isinstance(result, str)
            return result
        except ModelError:
            fallback = self.models["geral_leve"]
            if fallback != model:
                self.set_model(fallback)
                result = self._call_ollama(prompt, stream=False, model=fallback)
                assert isinstance(result, str)
                return result
            raise

    def ask(self, prompt: str, stream: bool = True, tools: list | None = None):
        """Unified ask method. Tools are accepted for future function-calling flows."""
        if tools:
            tool_text = "\n".join(f"- {t.get('name', 'tool')}: {t.get('description', '')}" for t in tools)
            prompt = f"{prompt}\n\nFerramentas disponíveis:\n{tool_text}"
        return self.ask_stream(prompt) if stream else self.ask_sync(prompt)
