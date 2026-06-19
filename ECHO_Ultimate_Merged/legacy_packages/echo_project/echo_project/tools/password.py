"""Password generator tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def password(length: int = 24, **kwargs) -> str:
    """Generate a strong random password."""
    try:
        import secrets, string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.?"
        return "".join(secrets.choice(alphabet) for _ in range(length))
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
