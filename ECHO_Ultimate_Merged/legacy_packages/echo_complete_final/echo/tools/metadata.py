from __future__ import annotations

from pathlib import Path
import os
from datetime import datetime

from core.exceptions import ToolException
from ._shared import json_pretty, sha256_file

def metadata(path: str) -> str:
    """Return file metadata, hashes, and basic technical info."""
    p = Path(path).expanduser()
    if not p.exists():
        raise ToolException(f"Path not found: {p}")
    stat = p.stat()
    info = {
        "path": str(p),
        "name": p.name,
        "suffix": p.suffix,
        "size_bytes": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "sha256": sha256_file(p) if p.is_file() else "",
        "is_file": p.is_file(),
        "is_dir": p.is_dir(),
    }
    if p.is_file():
        try:
            from PIL import Image
            img = Image.open(p)
            info["image"] = {"width": img.width, "height": img.height, "mode": img.mode}
        except Exception:
            pass
    return json_pretty(info)
