from __future__ import annotations

import requests
from tools._shared import json_dump
from core.config import CONFIG
from core.exceptions import ToolException

def image_gen(prompt: str, **kwargs) -> str:
    """Submit an image generation request to a local API if configured."""
    try:
        base = CONFIG.get("env", {}).get("image_gen_api_url", "")
        if not base:
            raise ToolException("IMAGE_GEN_API_URL is not configured")
        payload = {"prompt": prompt, **kwargs}
        r = requests.post(
            base.rstrip("/") + "/generate",
            json=payload,
            timeout=120,
            headers={"Authorization": CONFIG.get("env", {}).get("image_gen_api_key", "")},
        )
        r.raise_for_status()
        try:
            return json_dump(r.json())
        except Exception:
            return json_dump({"text": r.text[:12000]})
    except Exception as exc:
        raise ToolException(f"image_gen failed: {exc}")
