"""Image conversion tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def image_convert(path: str, format: str = "png", output_path: str | None = None, **kwargs) -> str:
    """Convert images between formats."""
    try:
        from pathlib import Path
        from PIL import Image
        src = Path(path)
        dest = Path(output_path) if output_path else src.with_suffix(f".{format.lower()}")
        img = Image.open(src)
        img.save(dest, format=format.upper())
        return str(dest)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
