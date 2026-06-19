"""Session memory management for ECHO."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import os

from core.config import CONFIG, BASE_DIR
from tools._common import safe_json_load, safe_json_dump, chunk_text


class Memory:
    """Persist and manage per-session message history."""

    def __init__(self, sessions_path: str | None = None):
        """Initialize memory storage."""
        self.sessions_dir = Path(sessions_path or CONFIG["context"]["history_path"])
        if not self.sessions_dir.is_absolute():
            self.sessions_dir = (BASE_DIR / self.sessions_dir).resolve()
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        """Return the file path for a session."""
        safe = "".join(c for c in session_id if c.isalnum() or c in ("-", "_"))
        return self.sessions_dir / f"{safe}.json"

    def save_session(self, session_id: str, messages: list[dict[str, str]]) -> str:
        """Save a session to disk."""
        path = self._path(session_id)
        safe_json_dump(path, messages)
        return str(path)

    def load_session(self, session_id: str) -> list[dict[str, str]]:
        """Load a session from disk."""
        path = self._path(session_id)
        if not path.exists():
            return []
        data = safe_json_load(path, [])
        return data if isinstance(data, list) else []

    def truncate(self, messages: list[dict[str, str]], max_tokens: int) -> list[dict[str, str]]:
        """Keep the newest messages that fit within the token budget."""
        if max_tokens <= 0:
            return messages[-1:] if messages else []
        kept: list[dict[str, str]] = []
        total_chars = 0
        for msg in reversed(messages):
            content = str(msg.get("content", ""))
            cost = len(content)
            if (total_chars + cost) / 4 > max_tokens and kept:
                break
            kept.append(msg)
            total_chars += cost
        return list(reversed(kept))

    def list_sessions(self) -> list[str]:
        """List available session identifiers."""
        return sorted(p.stem for p in self.sessions_dir.glob("*.json"))

    def delete_session(self, session_id: str) -> bool:
        """Delete a session from disk."""
        path = self._path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def summarize_session(self, messages: list[dict[str, str]], max_chars: int = 8000) -> str:
        """Create a compact textual summary of a message list."""
        lines = []
        for msg in messages:
            lines.append(f'{msg.get("role", "user")}: {msg.get("content", "")}')
        return chunk_text("\n".join(lines), max_chars=max_chars).__next__()
