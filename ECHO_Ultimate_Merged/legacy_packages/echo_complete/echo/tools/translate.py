import os
from typing import Any

import requests

from core.exceptions import ToolException

def translate(text: str, target_lang: str = "en", source_lang: str = "auto", endpoint: str = "") -> str:
    """Translate text using LibreTranslate or Google's public endpoint."""
    try:
        url = endpoint or os.getenv("LIBRETRANSLATE_URL", "").strip()
        if url:
            resp = requests.post(
                url.rstrip("/") + "/translate",
                json={"q": text, "source": source_lang, "target": target_lang, "format": "text"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("translatedText", "")
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text,
        }
        resp = requests.get("https://translate.googleapis.com/translate_a/single", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return "".join(part[0] for part in data[0] if part and part[0])
    except Exception as e:
        raise ToolException(f"Erro na ferramenta translate: {e}") from e
