from __future__ import annotations

from pathlib import Path
from tools._shared import download_stream, safe_filename, json_dump, sha256_bytes
from core.exceptions import ToolException

def download(url: str, dest_dir: str = "./temp", filename: str | None = None, **kwargs) -> str:
    """Download a URL to disk with checksum reporting."""
    try:
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        if not filename:
            name = url.split("?")[0].rstrip("/").split("/")[-1] or "download.bin"
            filename = safe_filename(name)
        target = dest / filename
        download_stream(url, target, timeout=kwargs.get("timeout", 90))
        data = target.read_bytes()
        return json_dump({
            "path": str(target),
            "bytes": len(data),
            "sha256": sha256_bytes(data),
        })
    except Exception as exc:
        raise ToolException(f"download failed: {exc}")
