from __future__ import annotations

from pathlib import Path
import json

from .db import Database

def chunk_text(text: str, size: int = 1200):
    for i in range(0, len(text), size):
        yield text[i:i + size]

class KnowledgeBase:
    def __init__(self, config):
        self.config = config
        self.base = Path(config.storage.kb_dir)
        self.base.mkdir(parents=True, exist_ok=True)
        self.db = Database(Path(config.storage.db_path))

    def ingest_text(self, source: str, text: str, metadata: dict | None = None):
        metadata = metadata or {}
        chunks = list(chunk_text(text))
        with self.db.conn() as con:
            con.execute("DELETE FROM knowledge_chunks WHERE source=?", (source,))
            for idx, chunk in enumerate(chunks):
                con.execute(
                    "INSERT INTO knowledge_chunks(source, chunk_index, content, metadata) VALUES(?,?,?,?)",
                    (source, idx, chunk, json.dumps(metadata, ensure_ascii=False)),
                )

    def search(self, query: str, limit: int = 5):
        q = query.lower()
        with self.db.conn() as con:
            rows = con.execute("SELECT source, chunk_index, content, metadata FROM knowledge_chunks").fetchall()
        scored = []
        for r in rows:
            content = r["content"]
            score = sum(1 for token in q.split() if token in content.lower())
            if score:
                scored.append((score, r))
        scored.sort(key=lambda x: (-x[0], len(x[1]["content"])))
        return scored[:limit]
