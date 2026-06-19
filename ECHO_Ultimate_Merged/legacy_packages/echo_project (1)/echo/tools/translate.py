"""Translation helper."""

from __future__ import annotations
from tools._common import ToolException

def translate(text: str, target_language: str = "pt") -> str:
    """Translate text using deep-translator if available."""
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="auto", target=target_language).translate(text)
    except Exception as e:
        raise ToolException(f"Falha na tradução: {e}")
