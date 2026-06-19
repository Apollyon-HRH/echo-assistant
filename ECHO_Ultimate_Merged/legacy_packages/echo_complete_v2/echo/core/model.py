from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Generator

import requests

from core.config import CONFIG

KEYWORDS_CODE = {
    "código", "função", "script", "debug", "algoritmo", "parser", "compilador",
    "injetar", "exploit", "buffer", "overflow", "reverse", "engenharia reversa",
    "assembly", "ponteiro", "malloc", "fork", "thread", "socket", "payload", "shellcode"
}
KEYWORDS_GENERAL = {
    "explique", "detalhe", "teoria", "história", "filosofia", "por que", "como funciona", "significado"
}

@dataclass
class ModelDecision:
    model_key: str
    model_name: str

class ModelManager:
    """Single-model Ollama manager with smart routing and fallback."""

    def __init__(self, model_name: str, context_length: int = 8192, system_prompt: str | None = None):
        self.context_length = context_length
        self.system_prompt = system_prompt or CONFIG["system_prompt"]
        self.models = CONFIG["models"]
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        self.model_key = self._reverse_lookup(model_name)
        self.model = self.models.get(self.model_key, model_name)
        self.fallback_key = "geral_leve"

    def _reverse_lookup(self, model_name: str) -> str:
        for key, value in self.models.items():
            if value == model_name:
                return key
        return CONFIG["models"].get("default", "geral_leve")

    def _count_words(self, prompt: str) -> int:
        return len(re.findall(r"\S+", prompt))

    def choose_model(self, prompt: str, manual: str | None = None) -> ModelDecision:
        if manual in {"gp", "geral_pesado"}:
            return ModelDecision("geral_pesado", self.models["geral_pesado"])
        if manual in {"gl", "geral_leve"}:
            return ModelDecision("geral_leve", self.models["geral_leve"])
        if manual in {"cp", "codigo_pesado"}:
            return ModelDecision("codigo_pesado", self.models["codigo_pesado"])
        if manual in {"cl", "codigo_leve"}:
            return ModelDecision("codigo_leve", self.models["codigo_leve"])

        lower = prompt.lower()
        words = self._count_words(prompt)
        if any(k in lower for k in KEYWORDS_CODE):
            return ModelDecision(
                "codigo_pesado" if words >= 10 else "codigo_leve",
                self.models["codigo_pesado"] if words >= 10 else self.models["codigo_leve"],
            )
        if any(k in lower for k in KEYWORDS_GENERAL):
            return ModelDecision("geral_pesado", self.models["geral_pesado"])
        if words > 30:
            return ModelDecision("geral_pesado", self.models["geral_pesado"])
        return ModelDecision("geral_leve", self.models["geral_leve"])

    def set_model(self, model_name: str) -> None:
        self.model_key = self._reverse_lookup(model_name)
        self.model = self.models.get(self.model_key, model_name)

    def _build_payload(self, prompt: str, stream: bool, tools: list | None = None) -> dict:
        return {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {"num_ctx": self.context_length},
        }

    def _call_ollama(self, prompt: str, stream: bool = True) -> requests.Response:
        payload = self._build_payload(prompt, stream)
        resp = requests.post(
            f"{self.ollama_host}/api/generate",
            json=payload,
            stream=stream,
            timeout=CONFIG["timeouts"]["ollama_request"],
        )
        resp.raise_for_status()
        return resp

    def _extract_text(self, prompt: str) -> str:
        prompt = prompt.strip()
        if self.system_prompt:
            return f"{self.system_prompt}\n\n{prompt}"
        return prompt

    def ask_stream(self, prompt: str) -> Generator[str, None, None]:
        try:
            resp = self._call_ollama(self._extract_text(prompt), stream=True)
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
                if data.get("done"):
                    break
        except Exception:
            if self.model_key != self.fallback_key:
                self.set_model(self.models[self.fallback_key])
                yield from self.ask_stream(prompt)
            else:
                raise

    def ask_sync(self, prompt: str) -> str:
        try:
            resp = self._call_ollama(self._extract_text(prompt), stream=False)
            data = resp.json()
            return data.get("response", "")
        except Exception:
            if self.model_key != self.fallback_key:
                self.set_model(self.models[self.fallback_key])
                return self.ask_sync(prompt)
            raise

    def ask(self, prompt: str, stream: bool = True, tools: list | None = None):
        return self.ask_stream(prompt) if stream else self.ask_sync(prompt)
