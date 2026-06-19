from __future__ import annotations

from pathlib import Path

from core.exceptions import ToolException

def image_convert(input_path: str, output_path: str, format: str = "PNG", resize: str | None = None) -> str:
    """Convert images between formats and optionally resize them."""
    inp = Path(input_path).expanduser()
    out = Path(output_path).expanduser()
    if not inp.exists():
        raise ToolException(f"Image not found: {inp}")
    try:
        from PIL import Image
        img = Image.open(inp)
        if resize:
            w, h = [int(x) for x in resize.lower().replace("x", ",").split(",")[:2]]
            img = img.resize((w, h))
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out, format=format.upper())
        return str(out)
    except Exception as exc:
        raise ToolException(f"image_convert failed: {exc}") from exc
