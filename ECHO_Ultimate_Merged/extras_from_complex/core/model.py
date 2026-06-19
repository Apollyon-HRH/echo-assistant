from __future__ import annotations

from dataclasses import dataclass
import os
import requests

@dataclass
class RoutedModel:
    name: str
    reason: str

class ModelRouter:
    def __init__(self, config, memory=None):
        self.config = config
        self.memory = memory
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def choose(self, prompt: str) -> RoutedModel:
        text = prompt.lower()
        code_keywords = self.config.routing.get("code_keywords", [])
        heavy_keywords = self.config.routing.get("heavy_general_keywords", [])
        word_count = len(prompt.split())

        if any(k.lower() in text for k in code_keywords):
            model = self.config.models["code_heavy"] if word_count >= 10 else self.config.models["code_light"]
            return RoutedModel(model, "code")
        if any(k.lower() in text for k in heavy_keywords) or word_count > 30:
            return RoutedModel(self.config.models["general_heavy"], "deep-general")
        return RoutedModel(self.config.models["general_light"], "light-general")

    def generate(self, prompt: str, session: list[dict] | None = None, stream: bool = False) -> str:
        routed = self.choose(prompt)
        messages = session or []
        context = "\n".join(f'{m["role"]}: {m["content"]}' for m in messages[-8:])
        full = f"{context}\nuser: {prompt}".strip()

        payload = {
            "model": routed.name,
            "prompt": full,
            "stream": stream,
            "options": {"num_ctx": int(self.config.routing.get("max_context_tokens", 8192))},
        }

        r = requests.post(f"{self.host}/api/generate", json=payload, timeout=180)
        r.raise_for_status()

        if stream:
            chunks = []
            for line in r.iter_lines(decode_unicode=True):
                if line:
                    chunks.append(line)
            return "\n".join(chunks)

        data = r.json()
        return data.get("response", "")
