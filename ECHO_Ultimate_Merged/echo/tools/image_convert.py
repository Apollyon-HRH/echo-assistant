from __future__ import annotations

from pathlib import Path
from tools._shared import json_dump
from core.exceptions import ToolException

def image_convert(input_path: str, output_path: str, size: str | None = None, format: str | None = None, **kwargs) -> str:
    """Resize or convert images using Pillow."""
    try:
        from PIL import Image
        img = Image.open(input_path)
        if size and "x" in size:
            w, h = size.lower().split("x", 1)
            img = img.resize((int(w), int(h)))
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        save_kwargs = {}
        if format:
            save_kwargs["format"] = format.upper()
        img.save(out, **save_kwargs)
        return json_dump({"input": input_path, "output": str(out)})
    except Exception as exc:
        raise ToolException(f"image_convert failed: {exc}")
