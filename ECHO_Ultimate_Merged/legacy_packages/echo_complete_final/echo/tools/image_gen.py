from __future__ import annotations

from pathlib import Path

import requests

from core.config import CONFIG
from core.exceptions import ToolException
from ._shared import TEMP_DIR, ensure_parent

def image_gen(prompt: str, negative_prompt: str = "", width: int = 1024, height: int = 1024, steps: int = 25, output_path: str | None = None) -> str:
    """Generate an image using a configured Stable Diffusion-compatible backend."""
    prompt = prompt.strip()
    if not prompt:
        raise ToolException("prompt cannot be empty")

    out = Path(output_path).expanduser() if output_path else TEMP_DIR / "generated.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    env = CONFIG.get("env", {})
    api_url = env.get("a1111_url")
    api_key = env.get("a1111_api_key")

    if not api_url:
        # fallback placeholder image so the function always returns a usable artifact
        try:
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (width, height), "white")
            d = ImageDraw.Draw(img)
            d.text((20, 20), prompt[:200], fill="black")
            img.save(out)
            return str(out)
        except Exception as exc:
            raise ToolException(f"No image backend configured and fallback failed: {exc}") from exc

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "steps": steps,
    }
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        r = requests.post(f"{api_url.rstrip('/')}/sdapi/v1/txt2img", json=payload, headers=headers, timeout=300)
        r.raise_for_status()
        data = r.json()
        if not data.get("images"):
            raise ToolException("Image backend returned no images")
        import base64
        img_bytes = base64.b64decode(data["images"][0])
        out.write_bytes(img_bytes)
        return str(out)
    except Exception as exc:
        raise ToolException(f"image_gen failed: {exc}") from exc
