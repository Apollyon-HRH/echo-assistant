"""Code generation tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def code_gen(description: str, language: str = "python", **kwargs) -> str:
    """Generate a code skeleton from a description."""
    try:
        return f"# Language: {language}\n# Description: {description}\n\n"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
