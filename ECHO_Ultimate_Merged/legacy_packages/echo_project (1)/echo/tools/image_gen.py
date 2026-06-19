"""Local image generation bridge."""

from __future__ import annotations
import os
from pathlib import Path
import base64
import requests

from tools._common import ToolException, TEMP_DIR, ensure_parent

def image_gen(prompt: str, output_path: str | None = None, width: int = 1024, height: int = 1024) -> str:
    """Generate an image using a configured local service."""
    endpoint = os.getenv("IMAGE_GEN_URL", "").strip()
    if not endpoint:
        raise ToolException("IMAGE_GEN_URL não configurado no .env.")
    out = Path(output_path) if output_path else TEMP_DIR / "generated_image.png"
    ensure_parent(out)
    payload = {"prompt": prompt, "width": width, "height": height}
    try:
        r = requests.post(endpoint, json=payload, timeout=180)
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        if "application/json" in ct:
            data = r.json()
            if "image_base64" in data:
                out.write_bytes(base64.b64decode(data["image_base64"]))
            elif "image_url" in data:
                img = requests.get(data["image_url"], timeout=180)
                img.raise_for_status()
                out.write_bytes(img.content)
            else:
                raise ToolException("Resposta JSON sem imagem.")
        else:
            out.write_bytes(r.content)
        return str(out)
    except Exception as e:
        raise ToolException(f"Falha na geração de imagem: {e}")
