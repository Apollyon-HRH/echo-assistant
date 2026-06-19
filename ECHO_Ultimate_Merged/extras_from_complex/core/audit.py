from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json

@dataclass
class AuditEvent:
    ts: str
    kind: str
    actor: str
    target: str
    status: str
    details: dict

class AuditLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, kind: str, actor: str, target: str, status: str, details: dict | None = None):
        event = AuditEvent(
            ts=datetime.now(timezone.utc).isoformat(),
            kind=kind,
            actor=actor,
            target=target,
            status=status,
            details=details or {},
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
