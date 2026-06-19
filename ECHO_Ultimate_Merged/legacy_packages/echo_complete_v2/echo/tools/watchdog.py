from __future__ import annotations

import time
from pathlib import Path

from tools._base import ToolException

def watchdog(path: str, duration: int = 10) -> str:
    """Watch a directory for changes by polling."""
    try:
        root = Path(path)
        before = {p: p.stat().st_mtime for p in root.rglob("*") if p.is_file()}
        time.sleep(duration)
        after = {p: p.stat().st_mtime for p in root.rglob("*") if p.is_file()}
        changed = [str(p) for p in after if p not in before or before[p] != after[p]]
        return "\n".join(changed) if changed else "No changes detected."
    except Exception as e:
        raise ToolException(str(e)) from e
