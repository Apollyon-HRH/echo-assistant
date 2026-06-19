"""Cleanup temporary files and caches."""

from __future__ import annotations
from pathlib import Path
import time
import shutil

from tools._common import ToolException, TEMP_DIR, LOGS_DIR

def cleanup(action: str = "temp", older_than_days: int = 7) -> str:
    """Clean temp files or old logs."""
    base = TEMP_DIR if action == "temp" else LOGS_DIR
    removed = 0
    cutoff = time.time() - older_than_days * 86400
    try:
        for p in base.rglob("*"):
            try:
                if p.is_file() and p.stat().st_mtime < cutoff:
                    p.unlink()
                    removed += 1
            except Exception:
                pass
        return f"{removed} arquivos removidos de {base}"
    except Exception as e:
        raise ToolException(f"Falha no cleanup: {e}")
