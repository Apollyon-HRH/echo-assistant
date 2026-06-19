from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import uuid

from .db import Database

@dataclass
class Message:
    role: str
    content: str

class SessionMemory:
    def __init__(self, config):
        self.config = config
        self.base = Path(config.storage.session_dir)
        self.base.mkdir(parents=True, exist_ok=True)
        self.db = Database(Path(config.storage.db_path))

    def new_session(self, title: str = "chat") -> str:
        session_id = str(uuid.uuid4())
        self.save(session_id, [{"role": "system", "content": title}])
        return session_id

    def session_path(self, session_id: str) -> Path:
        return self.base / f"{session_id}.json"

    def save(self, session_id: str, messages: list[dict]):
        self.session_path(session_id).write_text(
            json.dumps(messages, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        with self.db.conn() as con:
            con.execute("INSERT OR IGNORE INTO sessions(id,title) VALUES(?,?)", (session_id, "chat"))
            con.execute("UPDATE sessions SET updated_at=CURRENT_TIMESTAMP WHERE id=?", (session_id,))
            con.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
            con.executemany(
                "INSERT INTO messages(session_id, role, content) VALUES(?,?,?)",
                [(session_id, m["role"], m["content"]) for m in messages],
            )

    def load(self, session_id: str) -> list[dict]:
        p = self.session_path(session_id)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return []

    def list_sessions(self) -> list[str]:
        return [p.stem for p in self.base.glob("*.json")]

    def truncate(self, messages: list[dict], max_tokens: int) -> list[dict]:
        budget = max_tokens * 4
        total = 0
        kept = []
        for m in reversed(messages):
            total += len(m.get("content", ""))
            kept.append(m)
            if total >= budget:
                break
        return list(reversed(kept))
