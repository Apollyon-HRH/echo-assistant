from __future__ import annotations

import os
import shutil
from pathlib import Path

from tools._base import ToolException

def directory(path: str, action: str = "list", target: str | None = None) -> str:
    """List, copy, move, or delete directories/files."""
    p = Path(path)
    try:
        if action == "list":
            return "\n".join(str(x) for x in sorted(p.iterdir()))
        if action == "copy" and target:
            shutil.copy2(p, target) if p.is_file() else shutil.copytree(p, target, dirs_exist_ok=True)
            return str(target)
        if action == "move" and target:
            shutil.move(str(p), target)
            return str(target)
        if action == "delete":
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink(missing_ok=True)
            return "deleted"
        raise ToolException("Unsupported action")
    except Exception as e:
        raise ToolException(str(e)) from e
