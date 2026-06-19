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


@dataclass
class RoutedModel:
    name: str
    reason: str


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
            return requests.post(url, json=payload, stream=stream, timeout=CONFIG.get("timeouts", {}).get("ollama_request", 120))
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


class ModelRouter:
    def __init__(self, config, memory=None):
        self.config = config
        self.memory = memory
        self.host = CONFIG.get("env", {}).get("ollama_base_url", "http://localhost:11434")
        self.manager = ModelManager(
            model_name=self._model_map().get("general_light", CONFIG.get("models", {}).get("default", "geral_leve")),
            context_length=int(self._routing().get("max_context_tokens", 8192)),
            system_prompt=CONFIG.get("system_prompt", ""),
        )

    def _models(self):
        if hasattr(self.config, "models"):
            return self.config.models
        return self.config.get("models", {})

    def _routing(self):
        if hasattr(self.config, "routing"):
            return self.config.routing
        return self.config.get("routing", {})

    def _model_map(self):
        models = self._models()
        return {
            "general_heavy": models.get("geral_pesado") or models.get("general_heavy") or models.get("default"),
            "general_light": models.get("geral_leve") or models.get("general_light") or models.get("default"),
            "code_heavy": models.get("codigo_pesado") or models.get("code_heavy") or models.get("default"),
            "code_light": models.get("codigo_leve") or models.get("code_light") or models.get("default"),
        }

    def choose(self, prompt: str) -> RoutedModel:
        text = prompt.lower()
        routing = self._routing()
        code_keywords = routing.get("code_keywords", [])
        heavy_keywords = routing.get("heavy_general_keywords", routing.get("heavy_keywords", []))
        word_count = len(prompt.split())

        if any(k.lower() in text for k in code_keywords):
            model = self._model_map()["code_heavy"] if word_count >= 10 else self._model_map()["code_light"]
            return RoutedModel(model, "code")
        if any(k.lower() in text for k in heavy_keywords) or word_count > 30:
            return RoutedModel(self._model_map()["general_heavy"], "deep-general")
        return RoutedModel(self._model_map()["general_light"], "light-general")

    def generate(self, prompt: str, session: list[dict] | None = None, stream: bool = False):
        routed = self.choose(prompt)
        self.manager.set_model(routed.name)
        if session:
            prefix = []
            for turn in session[-12:]:
                role = turn.get("role", "user").upper()
                content = str(turn.get("content", ""))
                prefix.append(f"{role}: {content}")
            prompt = "\n\n".join(prefix + [f"USER: {prompt}", "ASSISTANT:"])
        if stream:
            return self.manager.ask_stream(prompt)
        reply = self.manager.ask(prompt)
        return reply.text
