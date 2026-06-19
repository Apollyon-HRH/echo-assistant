from __future__ import annotations

from pathlib import Path
import json

import yaml

from tools._base import ToolException

def filesystem(path: str, content: str | None = None) -> str:
    """Read or write a file depending on the presence of content."""
    p = Path(path)
    try:
        if content is None:
            if not p.exists():
                raise ToolException(f"file not found: {path}")
            return p.read_text(encoding="utf-8", errors="ignore")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return str(p)
    except Exception as e:
        raise ToolException(str(e)) from e
