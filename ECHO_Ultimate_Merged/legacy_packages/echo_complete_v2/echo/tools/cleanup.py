from __future__ import annotations

import os
import shutil
from pathlib import Path

from tools._base import ToolException

def cleanup(path: str | None = None) -> str:
    """Remove temporary files from a path or system temp."""
    try:
        target = Path(path) if path else Path(os.getenv("TEMP", "/tmp"))
        removed = 0
        for p in target.glob("*"):
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                removed += 1
            except Exception:
                pass
        return f"removed={removed}"
    except Exception as e:
        raise ToolException(str(e)) from e
