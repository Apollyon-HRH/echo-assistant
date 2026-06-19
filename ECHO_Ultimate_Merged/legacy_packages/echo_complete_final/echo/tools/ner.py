from __future__ import annotations

import re
from datetime import datetime

from core.exceptions import ToolException
from ._shared import json_pretty

def ner(text: str) -> str:
    """Rule-based named entity extraction for common entities."""
    text = text.strip()
    if not text:
        raise ToolException("text cannot be empty")
    entities = {
        "emails": re.findall(r"[\w.-]+@[\w.-]+\.[A-Za-z]{2,}", text),
        "urls": re.findall(r"https?://\S+", text),
        "dates": re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text),
        "numbers": re.findall(r"\b\d+(?:[.,]\d+)?\b", text),
    }
    return json_pretty(entities)
