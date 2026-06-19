from __future__ import annotations

from pathlib import Path
import shutil
from tools._shared import json_dump
from core.exceptions import ToolException

def cleanup(path: str = "./temp", dry_run: bool = True, **kwargs) -> str:
    """Delete temp content safely or report what would be removed."""
    try:
        p = Path(path)
        if not p.exists():
            return json_dump({"removed": [], "missing": str(p)})
        removed = []
        if dry_run:
            for item in p.rglob("*"):
                removed.append(str(item))
        else:
            shutil.rmtree(p)
        return json_dump({"dry_run": dry_run, "count": len(removed), "items": removed[:200]})
    except Exception as exc:
        raise ToolException(f"cleanup failed: {exc}")
