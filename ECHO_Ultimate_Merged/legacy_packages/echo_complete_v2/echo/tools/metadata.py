from __future__ import annotations

from pathlib import Path

from tools._base import ToolException

def metadata(path: str) -> str:
    """Extract simple metadata from an image or media file."""
    try:
        from PIL import Image
        p = Path(path)
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            img = Image.open(p)
            info = {"format": img.format, "size": img.size, "mode": img.mode}
            return str(info)
        return f"path={p}; size={p.stat().st_size} bytes"
    except Exception as e:
        raise ToolException(str(e)) from e
