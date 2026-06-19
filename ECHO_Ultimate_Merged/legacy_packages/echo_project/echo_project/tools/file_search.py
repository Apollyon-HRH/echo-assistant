"""Recursive file search tool."""

from __future__ import annotations

import json
import re
from pathlib import Path

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def file_search(root: str, query: str, use_regex: bool = False, **kwargs) -> str:
    """Search files recursively by name or content."""
    try:
        from pathlib import Path
        import re
        root_path = Path(root)
        matches = []
        for file_path in root_path.rglob("*"):
            if not file_path.is_file():
                continue
            if query.lower() in file_path.name.lower():
                matches.append(str(file_path))
                continue
            try:
                text = read_text_file(file_path)
                if use_regex:
                    if re.search(query, text, flags=re.IGNORECASE | re.MULTILINE):
                        matches.append(str(file_path))
                elif query.lower() in text.lower():
                    matches.append(str(file_path))
            except Exception:
                continue
        return json_dump(matches[:200])
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
