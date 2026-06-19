from __future__ import annotations

import math
import re
from collections import Counter

from core.exceptions import ToolException

def summarizer(text: str, sentences: int = 3) -> str:
    """Create an extractive summary using frequency scoring."""
    text = text.strip()
    if not text:
        raise ToolException("text cannot be empty")
    parts = re.split(r"(?<=[.!?])\s+", text)
    if len(parts) <= sentences:
        return text
    words = re.findall(r"\b\w+\b", text.lower())
    freq = Counter(w for w in words if len(w) > 2)
    scored = []
    for s in parts:
        score = sum(freq.get(w, 0) for w in re.findall(r"\b\w+\b", s.lower()))
        scored.append((score, s))
    top = [s for _, s in sorted(scored, key=lambda x: x[0], reverse=True)[:sentences]]
    return " ".join(top)
