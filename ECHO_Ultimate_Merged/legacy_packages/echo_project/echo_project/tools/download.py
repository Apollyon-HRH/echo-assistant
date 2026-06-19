"""File download tool."""

from __future__ import annotations

import json
import tempfile

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def download(url: str, output_path: str | None = None, **kwargs) -> str:
    """Download a file to the temp folder or a custom path."""
    try:
        import tempfile
        from pathlib import Path
        url = normalize_url(url)
        if output_path:
            dest = Path(output_path)
        else:
            name = safe_filename(url.split("/")[-1] or "download.bin")
            dest = Path(tempfile.gettempdir()) / name
        return download_stream(url, dest, timeout=60)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
