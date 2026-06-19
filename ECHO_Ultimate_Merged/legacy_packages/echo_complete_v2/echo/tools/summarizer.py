from __future__ import annotations

from tools._base import ToolException

def summarizer(text: str, max_sentences: int = 5) -> str:
    """Heuristic text summarizer."""
    try:
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        return ". ".join(sentences[:max_sentences]) + ("." if sentences else "")
    except Exception as e:
        raise ToolException(str(e)) from e
