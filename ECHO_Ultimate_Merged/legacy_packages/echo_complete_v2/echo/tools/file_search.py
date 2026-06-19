from __future__ import annotations

import re
from pathlib import Path

from tools._base import ToolException

def file_search(path: str, pattern: str, recursive: bool = True, regex: bool = False) -> str:
    """Search files by name or content."""
    try:
        root = Path(path)
        hits = []
        iterator = root.rglob("*") if recursive else root.glob("*")
        for p in iterator:
            if not p.is_file():
                continue
            target = p.read_text(encoding="utf-8", errors="ignore")
            if regex:
                if re.search(pattern, target, re.I | re.M):
                    hits.append(str(p))
            else:
                if pattern.lower() in p.name.lower() or pattern.lower() in target.lower():
                    hits.append(str(p))
        return "\n".join(hits[:200]) or "No matches."
    except Exception as e:
        raise ToolException(str(e)) from e
