"""Log analyzer tool."""

from __future__ import annotations

import json
import re
from pathlib import Path

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def log_analyzer(path: str, pattern: str = "", limit: int = 200, **kwargs) -> str:
    """Search logs for patterns and summarize matches."""
    try:
        from pathlib import Path
        text = read_text_file(Path(path))
        lines = text.splitlines()
        if pattern:
            lines = [line for line in lines if pattern.lower() in line.lower()]
        return "\n".join(lines[:limit])
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
