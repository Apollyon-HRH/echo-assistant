"""Extractive summarization helper."""

from __future__ import annotations
from collections import Counter
import re

from tools._common import ToolException, clamp_text

def summarizer(text: str, sentences: int = 3) -> str:
    """Summarize text using a simple frequency-based extractor."""
    try:
        cleaned = text.strip()
        if not cleaned:
            raise ToolException("Texto vazio.")
        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", cleaned.lower())
        freq = Counter(words)
        scored = []
        for idx, sent in enumerate(parts):
            score = sum(freq[w] for w in re.findall(r"[A-Za-zÀ-ÿ0-9]+", sent.lower()))
            scored.append((score, idx, sent))
        best = [s for _, _, s in sorted(scored, reverse=True)[:sentences]]
        best.sort(key=lambda s: parts.index(s))
        return " ".join(best)
    except Exception as e:
        raise ToolException(f"Falha no summarizer: {e}")
