"""Sentiment analysis tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def sentiment(text: str, **kwargs) -> str:
    """Run sentiment analysis using TextBlob or VADER."""
    try:
        try:
            from textblob import TextBlob
            polarity = TextBlob(text).sentiment.polarity
            return json_dump({"polarity": polarity})
        except Exception:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            return json_dump(analyzer.polarity_scores(text))
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
