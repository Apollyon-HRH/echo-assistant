from __future__ import annotations

import re
from pathlib import Path
from typing import List

from core.exceptions import ToolException
from ._shared import json_pretty, read_text, list_files_recursive, normalize_text

def file_search(root: str, query: str, content: bool = False, regex: bool = False, limit: int = 50) -> str:
    """Search recursively by filename or file content."""
    root_path = Path(root).expanduser()
    if not root_path.exists():
        raise ToolException(f"Root not found: {root_path}")
    query = query.strip()
    if not query:
        raise ToolException("query cannot be empty")

    results = []
    pattern = re.compile(query, re.I) if regex else None
    for path in list_files_recursive(root_path):
        hay = str(path)
        matched = False
        if regex:
            matched = bool(pattern.search(hay))
        else:
            matched = query.lower() in hay.lower()
        if not matched and content:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                if regex:
                    matched = bool(pattern.search(text))
                else:
                    matched = query.lower() in text.lower()
            except Exception:
                continue
        if matched:
            results.append(str(path))
        if len(results) >= limit:
            break
    return json_pretty(results)
