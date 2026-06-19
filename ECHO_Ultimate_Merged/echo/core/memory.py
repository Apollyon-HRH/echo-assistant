
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

from .config import CONFIG
from .exceptions import ECHOError
from .logger import setup_logger

logger = setup_logger("echo.memory")

@dataclass
class SessionSnapshot:
    session_id: str
    created_at: float
    updated_at: float
    turns: List[Dict[str, Any]]
    summary: str = ""

class Memory:
    """Persist conversation sessions and lightweight summaries."""

    def __init__(self) -> None:
        self.session_dir = Path(CONFIG.get("context", {}).get("history_path", "./sessions/"))
        self.memory_dir = Path(CONFIG.get("context", {}).get("memory_path", "./memory/"))
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self.session_dir / f"{session_id}.json"

    def _summary_path(self, session_id: str) -> Path:
        return self.memory_dir / f"{session_id}.summary.txt"

    def load_session(self, session_id: str) -> List[Dict[str, Any]]:
        path = self._path(session_id)
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("turns", [])
        except Exception as exc:
            raise ECHOError(f"Could not load session {session_id}: {exc}") from exc

    def save_session(self, session_id: str, turns: List[Dict[str, Any]], summary: str = "") -> str:
        now = time.time()
        snapshot = SessionSnapshot(session_id=session_id, created_at=now, updated_at=now, turns=turns, summary=summary)
        path = self._path(session_id)
        path.write_text(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        if summary:
            self._summary_path(session_id).write_text(summary, encoding="utf-8")
        return str(path)

    def append_turn(self, turns: List[Dict[str, Any]], role: str, content: str, **meta: Any) -> None:
        turns.append({"role": role, "content": content, "meta": meta, "ts": time.time()})

    def summarize_turns(self, turns: List[Dict[str, Any]], max_chars: int = 2200) -> str:
        joined = []
        for turn in turns[-12:]:
            role = turn.get("role", "user").upper()
            content = str(turn.get("content", "")).strip().replace("\n", " ")
            joined.append(f"{role}: {content}")
        return "\n".join(joined)[:max_chars]

    def trim_turns(self, turns: List[Dict[str, Any]], max_turns: int) -> List[Dict[str, Any]]:
        if len(turns) <= max_turns:
            return turns
        summary = self.summarize_turns(turns[:-max_turns])
        kept = turns[-max_turns:]
        if summary:
            kept = [{"role": "system", "content": f"Resumo de contexto anterior: {summary}"}] + kept
        return kept

    def list_sessions(self) -> List[str]:
        return sorted(p.stem for p in self.session_dir.glob("*.json"))

    def delete_session(self, session_id: str) -> bool:
        removed = False
        for path in [self._path(session_id), self._summary_path(session_id)]:
            if path.exists():
                path.unlink()
                removed = True
        return removed
