"""Image generation tool."""

from __future__ import annotations

import json
import tempfile

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def image_gen(prompt: str, output_path: str | None = None, **kwargs) -> str:
    """Generate an image using a local or API backend if configured."""
    try:
        from pathlib import Path
        import tempfile
        out = Path(output_path or (Path(tempfile.gettempdir()) / "echo_image.png"))
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Optional local backend: use Pillow placeholder if no generator is configured.
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new("RGB", (1024, 1024), color="white")
            draw = ImageDraw.Draw(img)
            draw.text((40, 40), prompt[:1000], fill="black")
            img.save(out)
            return str(out)
        except Exception:
            raise ToolException("Image generation backend unavailable")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
