from __future__ import annotations

import re
from collections import Counter
from tools._shared import json_dump
from core.exceptions import ToolException

def summarizer(text: str, sentences: int = 5, **kwargs) -> str:
    """Create an extractive summary using sentence scoring."""
    try:
        raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        words = re.findall(r"\w+", text.lower())
        freq = Counter(w for w in words if len(w) > 3)
        scored = []
        for idx, sent in enumerate(raw_sentences):
            score = sum(freq.get(w, 0) for w in re.findall(r"\w+", sent.lower()))
            scored.append((score, idx, sent))
        chosen = [s for _, _, s in sorted(scored, reverse=True)[:sentences]]
        chosen = sorted(chosen, key=lambda s: raw_sentences.index(s))
        return json_dump({"summary": " ".join(chosen), "sentences": chosen})
    except Exception as exc:
        raise ToolException(f"summarizer failed: {exc}")
