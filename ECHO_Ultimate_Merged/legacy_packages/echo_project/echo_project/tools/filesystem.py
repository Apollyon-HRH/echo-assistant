"""Filesystem read/write tool."""

from __future__ import annotations

import json
from pathlib import Path

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def filesystem(path: str, content: str | None = None, **kwargs) -> str:
    """Read or write a single file."""
    try:
        from pathlib import Path
        p = Path(path)
        if content is None:
            return read_text_file(p)
        return write_text_file(p, content)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
