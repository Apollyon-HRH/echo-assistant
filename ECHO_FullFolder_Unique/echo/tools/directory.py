from __future__ import annotations

from pathlib import Path
from tools._shared import json_dump
from core.exceptions import ToolException

def directory(path: str = ".", depth: int = 2, **kwargs) -> str:
    """Return a directory tree and summary statistics."""
    try:
        root = Path(path)
        entries = []
        for p in root.rglob("*"):
            rel = p.relative_to(root)
            if len(rel.parts) <= depth:
                entries.append({"path": str(rel), "type": "dir" if p.is_dir() else "file", "size": p.stat().st_size if p.is_file() else 0})
        return json_dump({"root": str(root), "entries": entries[:2000]})
    except Exception as exc:
        raise ToolException(f"directory failed: {exc}")
