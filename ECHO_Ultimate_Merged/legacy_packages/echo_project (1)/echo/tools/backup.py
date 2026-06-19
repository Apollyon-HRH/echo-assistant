"""Backup directories into zip archives."""

from __future__ import annotations
from pathlib import Path
import zipfile
import time

from tools._common import ToolException, ensure_parent

def backup(path: str, output: str | None = None) -> str:
    """Create a zip backup of a file or directory."""
    p = Path(path).expanduser()
    out = Path(output) if output else p.with_name(f"{p.name}.backup.{int(time.time())}.zip")
    ensure_parent(out)
    try:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            if p.is_dir():
                for item in p.rglob("*"):
                    if item.is_file():
                        zf.write(item, item.relative_to(p.parent))
            else:
                zf.write(p, p.name)
        return str(out)
    except Exception as e:
        raise ToolException(f"Falha no backup: {e}")
