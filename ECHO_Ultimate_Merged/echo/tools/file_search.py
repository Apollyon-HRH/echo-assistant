from __future__ import annotations

from pathlib import Path
import re
from tools._shared import json_dump
from core.exceptions import ToolException

def file_search(root: str, pattern: str, glob: str = "**/*", limit: int = 200, **kwargs) -> str:
    """Search text within files using regex."""
    try:
        base = Path(root)
        rx = re.compile(pattern)
        matches = []
        for p in base.glob(glob):
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    matches.append({"file": str(p), "line": i, "text": line[:500]})
                    if len(matches) >= limit:
                        return json_dump(matches)
        return json_dump(matches)
    except Exception as exc:
        raise ToolException(f"file_search failed: {exc}")
