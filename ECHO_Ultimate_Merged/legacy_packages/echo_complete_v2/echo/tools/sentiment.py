from __future__ import annotations

from tools._base import ToolException

def sentiment(text: str) -> str:
    """Simple sentiment analysis."""
    try:
        from textblob import TextBlob
        pol = TextBlob(text).sentiment.polarity
        label = "positive" if pol > 0.1 else "negative" if pol < -0.1 else "neutral"
        return f"{label} ({pol:.3f})"
    except Exception as e:
        raise ToolException(str(e)) from e
