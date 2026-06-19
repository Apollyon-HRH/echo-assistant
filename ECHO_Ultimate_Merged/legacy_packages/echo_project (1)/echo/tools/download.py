"""Download remote files to disk."""

from __future__ import annotations
from pathlib import Path
import requests

from tools._common import ToolException, ensure_parent, guess_filename_from_url, TEMP_DIR

def download(url: str, output_path: str | None = None) -> str:
    """Download a URL to a local file."""
    try:
        out = Path(output_path) if output_path else TEMP_DIR / guess_filename_from_url(url)
        ensure_parent(out)
        with requests.get(url, stream=True, timeout=60, headers={"User-Agent":"Mozilla/5.0"}) as r:
            r.raise_for_status()
            with out.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return str(out)
    except Exception as e:
        raise ToolException(f"Falha no download: {e}")
