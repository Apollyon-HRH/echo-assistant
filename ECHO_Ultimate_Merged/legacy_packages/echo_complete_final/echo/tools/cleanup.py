from __future__ import annotations

import time
from pathlib import Path

from core.config import CONFIG
from core.exceptions import ToolException

def cleanup(path: str | None = None, older_than_days: int = 30) -> str:
    """Remove old files from a directory tree."""
    root = Path(path or CONFIG["runtime"]["temp_path"]).expanduser()
    if not root.exists():
        raise ToolException(f"Path not found: {root}")
    cutoff = time.time() - older_than_days * 86400
    removed = 0
    for p in root.rglob("*"):
        if p.is_file() and p.stat().st_mtime < cutoff:
            p.unlink()
            removed += 1
    return f"Removed {removed} files"
