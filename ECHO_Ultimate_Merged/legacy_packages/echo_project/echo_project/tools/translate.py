"""Translation tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def translate(text: str, target_lang: str = "en", source_lang: str = "auto", **kwargs) -> str:
    """Translate text using LibreTranslate or a local fallback."""
    try:
        import requests
        endpoint = kwargs.get("endpoint") or "https://libretranslate.com/translate"
        payload = {"q": text, "source": source_lang, "target": target_lang, "format": "text"}
        resp = requests.post(endpoint, json=payload, timeout=60)
        if resp.status_code >= 400:
            return text
        data = resp.json()
        return data.get("translatedText", text)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
