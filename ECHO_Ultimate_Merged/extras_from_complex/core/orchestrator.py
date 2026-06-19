from __future__ import annotations

from dataclasses import dataclass
import time

@dataclass
class OrchestratedResponse:
    text: str
    model: str
    routing_reason: str
    latency_ms: int

class Orchestrator:
    def __init__(self, config, router, memory, plugins, permissions, tasks):
        self.config = config
        self.router = router
        self.memory = memory
        self.plugins = plugins
        self.permissions = permissions
        self.tasks = tasks

    def chat(self, session_id: str, prompt: str) -> OrchestratedResponse:
        started = time.time()
        session = self.memory.load(session_id)
        response = self.router.generate(prompt, session=session, stream=False)
        routed = self.router.choose(prompt)
        session.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response},
        ])
        session = self.memory.truncate(session, int(self.config.routing.get("max_context_tokens", 8192)))
        self.memory.save(session_id, session)
        latency = int((time.time() - started) * 1000)
        return OrchestratedResponse(response, routed.name, routed.reason, latency)
