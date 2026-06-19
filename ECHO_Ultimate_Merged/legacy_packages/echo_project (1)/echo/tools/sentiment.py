"""Sentiment analysis."""

from __future__ import annotations
import json

from tools._common import ToolException

def sentiment(text: str) -> str:
    """Return sentiment polarity and subjectivity."""
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        return json.dumps({"polarity": blob.sentiment.polarity, "subjectivity": blob.sentiment.subjectivity}, ensure_ascii=False)
    except Exception as e:
        raise ToolException(f"Falha em sentiment: {e}")
