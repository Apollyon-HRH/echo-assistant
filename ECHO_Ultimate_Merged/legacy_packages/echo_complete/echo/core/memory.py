"""Persistent session memory for ECHO."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .config import CONFIG

Message = Dict[str, str]

class Memory:
    """Store and load conversation sessions as JSON."""

    def __init__(self, base_path: str | Path | None = None) -> None:
        """Create a memory manager."""
        self.base_path = Path(base_path or CONFIG["context"]["history_path"])
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        """Return the JSON file path for a session."""
        safe = "".join(ch for ch in str(session_id) if ch.isalnum() or ch in ("-", "_"))
        return self.base_path / f"{safe}.json"

    def save_session(self, session_id: str, messages: List[Message]) -> Path:
        """Save a list of chat messages."""
        path = self._path(session_id)
        path.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load_session(self, session_id: str) -> List[Message]:
        """Load a saved session or return an empty list."""
        path = self._path(session_id)
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []

    def truncate(self, messages: List[Message], max_tokens: int) -> List[Message]:
        """Trim old messages until the approximate token budget fits."""
        budget_chars = max_tokens * 4
        kept: List[Message] = []
        total = 0
        for message in reversed(messages):
            total += len(message.get("content", ""))
            if total > budget_chars:
                break
            kept.append(message)
        return list(reversed(kept))

    def list_sessions(self) -> List[str]:
        """List all session identifiers on disk."""
        return sorted(p.stem for p in self.base_path.glob("*.json"))

    def delete_session(self, session_id: str) -> bool:
        """Delete a saved session."""
        path = self._path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False
