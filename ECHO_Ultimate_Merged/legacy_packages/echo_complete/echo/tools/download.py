from pathlib import Path

import requests

from core.exceptions import ToolException
from tools._shared import ensure_parent, safe_filename

def download(url: str, output_path: str | None = None) -> str:
    """Download a file from a URL with progress reporting."""
    try:
        target = Path(output_path) if output_path else Path("temp") / safe_filename(url.split("/")[-1] or "download.bin")
        ensure_parent(target)
        with requests.get(url, stream=True, timeout=60, headers={"User-Agent": "Mozilla/5.0"}) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            done = 0
            with target.open("wb") as fh:
                for chunk in resp.iter_content(chunk_size=1024 * 64):
                    if not chunk:
                        continue
                    fh.write(chunk)
                    done += len(chunk)
        return f"Arquivo baixado para {target} ({done} bytes, esperado {total} bytes)"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta download: {e}") from e
