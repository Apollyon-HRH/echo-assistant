from __future__ import annotations

import os
import requests

from tools._base import ToolException

def translate(text: str, target_lang: str = "en", source_lang: str = "auto") -> str:
    """Translate text using LibreTranslate if configured, else Google unofficial endpoint."""
    base = os.getenv("LIBRETRANSLATE_URL", "").rstrip("/")
    try:
        if base:
            r = requests.post(f"{base}/translate", json={"q": text, "source": source_lang, "target": target_lang, "format": "text"}, timeout=60)
            r.raise_for_status()
            return r.json().get("translatedText", "")
        r = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": source_lang, "tl": target_lang, "dt": "t", "q": text},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        return "".join(part[0] for part in data[0] if part[0])
    except Exception as e:
        raise ToolException(str(e)) from e
