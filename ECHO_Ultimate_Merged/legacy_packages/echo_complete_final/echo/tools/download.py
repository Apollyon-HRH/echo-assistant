from __future__ import annotations

from pathlib import Path

import requests

from core.exceptions import ToolException
from ._shared import ensure_parent, human_size

def download(url: str, output_path: str | None = None, timeout: int = 60) -> str:
    """Download a remote file with streamed progress."""
    url = url.strip()
    if not url:
        raise ToolException("url cannot be empty")

    dest = Path(output_path).expanduser() if output_path else Path(url.split("?")[0]).name
    dest = Path(dest)
    if not dest.is_absolute():
        dest = Path.cwd() / dest

    ensure_parent(dest)
    try:
        with requests.get(url, stream=True, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"}) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", "0"))
            received = 0
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
                        received += len(chunk)
    except Exception as exc:
        raise ToolException(f"Download failed: {exc}") from exc

    size = human_size(dest.stat().st_size)
    return f"Downloaded {dest} ({size})"
