from __future__ import annotations

from tools._shared import json_dump
from core.exceptions import ToolException

POS = {"bom", "ótimo", "otimo", "excelente", "feliz", "gostei", "positivo", "legal", "melhor"}
NEG = {"ruim", "péssimo", "pessimo", "horrível", "horrivel", "triste", "odiei", "negativo", "pior"}

def sentiment(text: str, **kwargs) -> str:
    """Heuristic sentiment analysis with transparency."""
    try:
        tokens = {t.lower().strip(".,!?;:") for t in text.split()}
        score = len(tokens & POS) - len(tokens & NEG)
        label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
        return json_dump({"label": label, "score": score})
    except Exception as exc:
        raise ToolException(f"sentiment failed: {exc}")
