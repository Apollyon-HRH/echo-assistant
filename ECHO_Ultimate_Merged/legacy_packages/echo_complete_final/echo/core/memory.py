from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .config import CONFIG
from .exceptions import MemoryError
from .logger import setup_logger

logger = setup_logger("echo.memory")

class Memory:
    """Persisted session memory for ECHO."""

    def __init__(self, sessions_path: str | None = None):
        self.sessions_dir = Path(sessions_path or CONFIG["context"]["history_path"]).resolve()
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.json"

    def save_session(self, session_id: str, messages: List[Dict[str, str]]) -> str:
        """Save a list of {role, content} messages to disk."""
        path = self._path(session_id)
        path.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.debug("Saved session %s to %s", session_id, path)
        return str(path)

    def load_session(self, session_id: str) -> List[Dict[str, str]]:
        """Load a saved session from disk."""
        path = self._path(session_id)
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise MemoryError(f"Failed to load session {session_id}: {exc}") from exc

    def truncate(self, messages: List[Dict[str, str]], max_tokens: int) -> List[Dict[str, str]]:
        """Truncate messages using 4 chars ~= 1 token."""
        limit_chars = max_tokens * 4
        total = sum(len(m.get("content", "")) for m in messages)
        if total <= limit_chars:
            return messages
        kept = list(messages)
        while kept and sum(len(m.get("content", "")) for m in kept) > limit_chars:
            kept.pop(0)
        return kept

    def list_sessions(self) -> List[str]:
        """Return all saved session IDs."""
        return sorted(p.stem for p in self.sessions_dir.glob("*.json"))

    def delete_session(self, session_id: str) -> bool:
        """Delete a saved session."""
        path = self._path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def count_tokens_estimate(self, messages: List[Dict[str, str]]) -> int:
        """Estimate token count from messages."""
        chars = sum(len(m.get("content", "")) for m in messages)
        return max(1, chars // 4)

    def summarize_if_needed(self, messages: List[Dict[str, str]], max_tokens: int) -> List[Dict[str, str]]:
        """Simple local truncation without an LLM dependency."""
        return self.truncate(messages, max_tokens)
