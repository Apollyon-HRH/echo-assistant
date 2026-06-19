from __future__ import annotations

from core.config import CONFIG
from core.exceptions import ToolException
from ._shared import split_chunks

def telegram(text: str, limit: int = 3500) -> str:
    """Utility helper for Telegram message chunking."""
    if not text:
        raise ToolException("text cannot be empty")
    chunks = split_chunks(text, limit=limit)
    return "\n\n---\n\n".join(chunks)
