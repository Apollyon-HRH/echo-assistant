"""Read/write filesystem helper."""

from __future__ import annotations
from pathlib import Path

from tools._common import ToolException, ensure_parent

def filesystem(path: str, content: str | None = None) -> str:
    """Read a file or write content to a file."""
    p = Path(path).expanduser()
    try:
        if content is None:
            return p.read_text(encoding="utf-8")
        ensure_parent(p)
        p.write_text(content, encoding="utf-8")
        return f"Arquivo salvo em {p}"
    except Exception as e:
        raise ToolException(f"Falha no filesystem: {e}")
