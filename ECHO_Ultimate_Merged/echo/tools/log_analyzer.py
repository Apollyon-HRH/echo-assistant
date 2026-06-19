from __future__ import annotations

from pathlib import Path
from collections import Counter
from tools._shared import json_dump
from core.exceptions import ToolException

def log_analyzer(path: str, limit: int = 50, **kwargs) -> str:
    """Analyze logs for levels and recurring lines."""
    try:
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        counter = Counter(line for line in lines if "ERROR" in line or "WARN" in line or "INFO" in line)
        return json_dump({
            "file": path,
            "lines": len(lines),
            "top": counter.most_common(limit),
        })
    except Exception as exc:
        raise ToolException(f"log_analyzer failed: {exc}")
