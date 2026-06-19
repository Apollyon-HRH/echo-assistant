"""Session memory for ECHO."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from threading import Lock
from typing import Dict, List

from core.config import CONFIG


class Memory:
    """Persist and truncate conversation sessions."""

    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = Path(base_path or CONFIG.get("context", {}).get("history_path", "./sessions/"))
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _session_file(self, session_id: str) -> Path:
        return self.base_path / f"{session_id}.json"

    def save_session(self, session_id: str, messages: List[Dict[str, str]]) -> None:
        """Save a session message list to disk."""
        with self._lock:
            self._session_file(session_id).write_text(
                json.dumps(messages, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def load_session(self, session_id: str) -> List[Dict[str, str]]:
        """Load a saved session."""
        path = self._session_file(session_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def truncate(self, messages: List[Dict[str, str]], max_tokens: int) -> List[Dict[str, str]]:
        """Truncate oldest messages until the estimated token count fits."""
        if max_tokens <= 0:
            return messages[-1:] if messages else []
        kept = list(messages)
        while kept and self._estimate_tokens(kept) > max_tokens:
            kept.pop(0)
        return kept

    def list_sessions(self) -> List[str]:
        """List saved session ids."""
        return sorted(p.stem for p in self.base_path.glob("*.json"))

    def delete_session(self, session_id: str) -> None:
        """Delete a saved session file."""
        path = self._session_file(session_id)
        if path.exists():
            path.unlink()

    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        chars = sum(len(msg.get("content", "")) for msg in messages)
        return chars // 4 + 1
