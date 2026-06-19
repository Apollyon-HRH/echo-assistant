"""Metadata extractor tool."""

from __future__ import annotations

import json
import mimetypes

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def metadata(path: str, **kwargs) -> str:
    """Extract basic file metadata."""
    try:
        from pathlib import Path
        import os
        p = Path(path)
        stat = p.stat()
        info = {
            "path": str(p),
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "mime": mimetypes.guess_type(str(p))[0] or "application/octet-stream",
        }
        try:
            from PIL import Image
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
                with Image.open(p) as img:
                    info["width"], info["height"] = img.size
                    info["format"] = img.format
        except Exception:
            pass
        return json_dump(info)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
