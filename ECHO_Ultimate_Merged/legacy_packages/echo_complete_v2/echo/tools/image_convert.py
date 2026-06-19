from __future__ import annotations

from pathlib import Path

from PIL import Image

from tools._base import ToolException

def image_convert(path: str, output_format: str = "png") -> str:
    """Convert image formats."""
    try:
        src = Path(path)
        out = src.with_suffix(f".{output_format.lower().lstrip('.')}")
        img = Image.open(src)
        img.save(out)
        return str(out)
    except Exception as e:
        raise ToolException(str(e)) from e
