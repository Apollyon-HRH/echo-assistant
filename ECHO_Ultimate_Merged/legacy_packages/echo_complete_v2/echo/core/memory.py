from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

from core.config import CONFIG

class Memory:
    """Persist and manage chat sessions."""

    def __init__(self, history_path: str | None = None):
        self.history_dir = Path(history_path or CONFIG["context"]["history_path"])
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self.history_dir / f"{session_id}.json"

    def save_session(self, session_id: str, messages: List[Dict[str, str]]) -> None:
        self._path(session_id).write_text(
            json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load_session(self, session_id: str) -> List[Dict[str, str]]:
        path = self._path(session_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def truncate(self, messages: List[Dict[str, str]], max_tokens: int) -> List[Dict[str, str]]:
        limit_chars = max_tokens * 4
        total = 0
        kept = []
        for msg in reversed(messages):
            content = str(msg.get("content", ""))
            total += len(content)
            kept.append(msg)
            if total >= limit_chars:
                break
        return list(reversed(kept))

    def list_sessions(self) -> List[str]:
        return sorted(p.stem for p in self.history_dir.glob("*.json"))

    def delete_session(self, session_id: str) -> bool:
        path = self._path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False
