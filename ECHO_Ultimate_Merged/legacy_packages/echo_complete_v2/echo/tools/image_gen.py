from __future__ import annotations

import os
from pathlib import Path

from tools._base import ToolException
from tools._utils import TEMP, now_stamp

def image_gen(prompt: str, output_name: str | None = None) -> str:
    """Generate an image using a local or remote endpoint when available."""
    try:
        endpoint = os.getenv("IMAGE_GEN_URL", "").rstrip("/")
        out = TEMP / (output_name or f"image_{now_stamp()}.png")
        if endpoint:
            import requests
            r = requests.post(f"{endpoint}/generate", json={"prompt": prompt}, timeout=300)
            r.raise_for_status()
            if "image_url" in r.json():
                img = requests.get(r.json()["image_url"], timeout=120)
                img.raise_for_status()
                out.write_bytes(img.content)
                return str(out)
        raise ToolException("No image generation backend configured. Set IMAGE_GEN_URL.")
    except Exception as e:
        raise ToolException(str(e)) from e
