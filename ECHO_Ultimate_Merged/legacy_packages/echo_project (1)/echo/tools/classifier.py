"""Simple text classifier."""

from __future__ import annotations
import json

from tools._common import ToolException

def classifier(text: str, labels: str = "general,technical,personal,finance,news") -> str:
    """Classify text into broad heuristic categories."""
    try:
        label_list = [l.strip() for l in labels.split(",") if l.strip()]
        low = text.lower()
        scores = {label: 0 for label in label_list}
        for kw in ["code", "python", "script", "api", "debug", "function"]:
            if kw in low and "technical" in scores:
                scores["technical"] += 2
        for kw in ["money", "bank", "price", "stock", "crypto"]:
            if kw in low and "finance" in scores:
                scores["finance"] += 2
        for kw in ["news", "today", "breaking", "report"]:
            if kw in low and "news" in scores:
                scores["news"] += 2
        for kw in ["i ", "me ", "my ", "feel", "family"]:
            if kw in low and "personal" in scores:
                scores["personal"] += 1
        best = max(scores.items(), key=lambda kv: kv[1])[0] if scores else "general"
        return json.dumps({"label": best, "scores": scores}, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ToolException(f"Falha no classifier: {e}")
