"""Image conversion and resizing."""

from __future__ import annotations
from pathlib import Path
from PIL import Image

from tools._common import ToolException, ensure_parent

def image_convert(input_path: str, output_path: str, format: str | None = None, resize: str | None = None, quality: int = 92) -> str:
    """Convert images between formats and optionally resize them."""
    try:
        inp = Path(input_path)
        out = Path(output_path)
        ensure_parent(out)
        img = Image.open(inp)
        if resize:
            w, h = [int(x) for x in resize.lower().split("x", 1)]
            img = img.resize((w, h))
        fmt = format.upper() if format else out.suffix.replace(".", "").upper()
        save_kwargs = {"quality": quality} if fmt in {"JPEG", "JPG"} else {}
        img.save(out, format=fmt, **save_kwargs)
        return str(out)
    except Exception as e:
        raise ToolException(f"Falha na conversão de imagem: {e}")
