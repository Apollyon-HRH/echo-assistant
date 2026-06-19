from __future__ import annotations

import re
from pathlib import Path

from tools._base import ToolException

def log_analyzer(path: str, pattern: str = r"error|fail|denied|unauthorized") -> str:
    """Analyze logs for suspicious patterns."""
    try:
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="ignore")
        matches = re.findall(pattern, text, flags=re.I | re.M)
        return f"matches={len(matches)}"
    except Exception as e:
        raise ToolException(str(e)) from e
