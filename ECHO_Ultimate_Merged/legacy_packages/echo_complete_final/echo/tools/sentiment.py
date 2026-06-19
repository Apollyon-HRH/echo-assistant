from __future__ import annotations

import re

from core.exceptions import ToolException
from ._shared import json_pretty

POS = {"bom", "ótimo", "excelente", "feliz", "amor", "perfeito", "bom", "positivo", "incrível", "great", "good", "awesome"}
NEG = {"ruim", "péssimo", "triste", "ódio", "horrível", "negativo", "terrível", "bad", "awful", "hate"}

def sentiment(text: str) -> str:
    """Basic lexicon-based sentiment analysis."""
    text = text.lower()
    if not text.strip():
        raise ToolException("text cannot be empty")
    words = re.findall(r"\b\w+\b", text)
    pos = sum(1 for w in words if w in POS)
    neg = sum(1 for w in words if w in NEG)
    score = pos - neg
    label = "neutral"
    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    return json_pretty({"label": label, "score": score, "positive": pos, "negative": neg})
