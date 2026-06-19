from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from core.exceptions import ToolException
from ._shared import json_pretty

def log_analyzer(path: str, limit: int = 2000) -> str:
    """Analyze log lines and summarize severity distribution."""
    p = Path(path).expanduser()
    if not p.exists():
        raise ToolException(f"Log file not found: {p}")
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
    counts = Counter()
    for line in lines:
        if "ERROR" in line:
            counts["ERROR"] += 1
        elif "WARNING" in line:
            counts["WARNING"] += 1
        elif "INFO" in line:
            counts["INFO"] += 1
        elif "DEBUG" in line:
            counts["DEBUG"] += 1
    return json_pretty({"lines": len(lines), "counts": dict(counts), "tail": lines[-20:]})
