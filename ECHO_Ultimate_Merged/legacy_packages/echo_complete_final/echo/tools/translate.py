from __future__ import annotations

import requests

from core.config import CONFIG
from core.exceptions import ToolException

def translate(text: str, target_lang: str = "en", source_lang: str = "auto") -> str:
    """Translate text using LibreTranslate or a compatible endpoint."""
    text = text.strip()
    if not text:
        raise ToolException("text cannot be empty")

    url = CONFIG.get("env", {}).get("translate_url") or "https://libretranslate.com/translate"
    try:
        r = requests.post(url, json={
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text",
        }, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("translatedText") or data.get("translation") or str(data)
    except Exception as exc:
        raise ToolException(f"translate failed: {exc}") from exc
