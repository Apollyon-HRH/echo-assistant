"""Backup tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def backup(source: str, destination: str | None = None, **kwargs) -> str:
    """Create a ZIP backup of a file or directory."""
    try:
        from pathlib import Path
        import zipfile
        src = Path(source)
        dest = Path(destination or f"{src.name}_{now_iso().replace(':', '-')}.zip")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            if src.is_dir():
                for item in src.rglob("*"):
                    if item.is_file():
                        zf.write(item, item.relative_to(src.parent))
            else:
                zf.write(src, src.name)
        return str(dest)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
