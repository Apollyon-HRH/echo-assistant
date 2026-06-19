import os
from pathlib import Path

import requests

from core.exceptions import ToolException
from tools._shared import ensure_dir

def image_gen(prompt: str, output_path: str = "", api_url: str = "") -> str:
    """Generate an image through a local or remote Stable Diffusion-compatible API."""
    try:
        url = api_url or os.getenv("IMAGE_GEN_API_URL", "").strip()
        if not url:
            raise ToolException("IMAGE_GEN_API_URL não configurada")
        out = Path(output_path) if output_path else Path("temp") / "generated.png"
        ensure_dir(out.parent)
        payload = {"prompt": prompt}
        resp = requests.post(url.rstrip("/") + "/sdapi/v1/txt2img", json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        images = data.get("images", [])
        if not images:
            raise ToolException("API não retornou imagens")
        import base64
        out.write_bytes(base64.b64decode(images[0]))
        return f"Imagem gerada em {out}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta image_gen: {e}") from e
