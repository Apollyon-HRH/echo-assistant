from __future__ import annotations
from pathlib import Path

def filesystem(path: str, content: str | None = None) -> str:
    p = Path(path)
    if content is None:
        return p.read_text(encoding="utf-8")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"written:{p}"
