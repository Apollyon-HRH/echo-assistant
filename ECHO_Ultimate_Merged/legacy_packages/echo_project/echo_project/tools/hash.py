"""Hashing tool."""

from __future__ import annotations

import json
from pathlib import Path

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def hash(path_or_text: str, algorithm: str = "sha256", is_file: bool = False, **kwargs) -> str:
    """Generate a hash from text or file content."""
    try:
        import hashlib
        data = Path(path_or_text).read_bytes() if is_file else path_or_text.encode("utf-8")
        h = getattr(hashlib, algorithm.lower())()
        h.update(data)
        return h.hexdigest()
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
