from __future__ import annotations

import requests
from tools._shared import json_dump
from core.config import CONFIG
from core.exceptions import ToolException

def translate(text: str, source: str = "auto", target: str = "en", **kwargs) -> str:
    """Translate text using LibreTranslate when available, with a clear fallback."""
    try:
        url = CONFIG.get("env", {}).get("translate_url", "")
        if not url:
            raise ToolException("LIBRETRANSLATE_URL is not configured")
        payload = {"q": text, "source": source, "target": target, "format": "text"}
        r = requests.post(url.rstrip("/") + "/translate", json=payload, timeout=30)
        r.raise_for_status()
        return json_dump(r.json())
    except Exception as exc:
        raise ToolException(f"translate failed: {exc}")
