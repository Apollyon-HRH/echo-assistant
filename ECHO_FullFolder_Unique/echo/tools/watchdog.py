from __future__ import annotations

from pathlib import Path
import time
from tools._shared import json_dump
from core.exceptions import ToolException

def watchdog(path: str, seconds: int = 5, **kwargs) -> str:
    """Poll a file or folder and return a short change snapshot."""
    try:
        p = Path(path)
        before = {str(x): x.stat().st_mtime_ns for x in p.rglob("*")} if p.is_dir() else {str(p): p.stat().st_mtime_ns}
        time.sleep(min(seconds, 10))
        after = {str(x): x.stat().st_mtime_ns for x in p.rglob("*")} if p.is_dir() else {str(p): p.stat().st_mtime_ns}
        return json_dump({"before_count": len(before), "after_count": len(after), "changed": before != after})
    except Exception as exc:
        raise ToolException(f"watchdog failed: {exc}")
