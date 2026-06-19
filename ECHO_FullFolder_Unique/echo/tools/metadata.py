from __future__ import annotations

from pathlib import Path
from tools._shared import json_dump
from core.exceptions import ToolException

def metadata(path: str, **kwargs) -> str:
    """Return file metadata and EXIF when available."""
    try:
        p = Path(path)
        info = {"path": str(p), "size": p.stat().st_size, "mtime": p.stat().st_mtime}
        try:
            from PIL import Image
            img = Image.open(p)
            info["image_format"] = img.format
            info["image_size"] = img.size
        except Exception:
            pass
        return json_dump(info)
    except Exception as exc:
        raise ToolException(f"metadata failed: {exc}")
