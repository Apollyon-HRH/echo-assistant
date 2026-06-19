"""Analyze log files for errors and patterns."""

from __future__ import annotations
from pathlib import Path
from collections import Counter
import re

from tools._common import ToolException, clamp_text


def log_analyzer(path: str, top: int = 10) -> str:
    """Inspect a log file and summarize frequent issues."""
    p = Path(path).expanduser()
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        errors = [ln for ln in lines if re.search(r"error|exception|traceback|failed", ln, re.I)]
        counts = Counter(re.sub(r"\d+", "0", ln).strip() for ln in errors)
        out = [f"lines={len(lines)}", f"errors={len(errors)}", "top="]
        for msg, cnt in counts.most_common(top):
            out.append(f"- {cnt}x {clamp_text(msg, 220)}")
        return "\n".join(out)
    except Exception as e:
        raise ToolException(f"Falha no log analyzer: {e}")
