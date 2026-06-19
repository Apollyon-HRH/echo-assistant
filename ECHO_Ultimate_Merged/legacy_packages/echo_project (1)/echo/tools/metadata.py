"""File and image metadata extraction."""

from __future__ import annotations
from pathlib import Path
import os
import json
from datetime import datetime

from tools._common import ToolException

def metadata(path: str) -> str:
    """Return metadata about a file."""
    p = Path(path).expanduser()
    try:
        stat = p.stat()
        info = {
            "path": str(p),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(timespec="seconds"),
        }
        try:
            from PIL import Image
            img = Image.open(p)
            info["image"] = {"format": img.format, "size": img.size, "mode": img.mode}
            exif = getattr(img, "_getexif", lambda: None)()
            if exif:
                info["exif"] = {str(k): str(v) for k, v in exif.items()}
        except Exception:
            pass
        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ToolException(f"Falha em metadata: {e}")
