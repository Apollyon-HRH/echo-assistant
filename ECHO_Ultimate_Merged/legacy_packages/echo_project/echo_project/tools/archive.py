"""Archive management tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def archive(path: str, action: str = "zip", destination: str | None = None, **kwargs) -> str:
    """Compress or extract archives."""
    try:
        from pathlib import Path
        import tarfile, zipfile, gzip, shutil
        p = Path(path)
        if action == "zip":
            dest = Path(destination or (str(p) + ".zip"))
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
                if p.is_dir():
                    for child in p.rglob("*"):
                        if child.is_file():
                            zf.write(child, child.relative_to(p.parent))
                else:
                    zf.write(p, p.name)
            return str(dest)
        if action == "unzip":
            dest = Path(destination or p.with_suffix(""))
            dest.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(p, "r") as zf:
                zf.extractall(dest)
            return str(dest)
        if action == "tar":
            dest = Path(destination or (str(p) + ".tar.gz"))
            with tarfile.open(dest, "w:gz") as tf:
                tf.add(p, arcname=p.name)
            return str(dest)
        if action == "untar":
            dest = Path(destination or p.with_suffix(""))
            dest.mkdir(parents=True, exist_ok=True)
            with tarfile.open(p, "r:gz") as tf:
                tf.extractall(dest)
            return str(dest)
        raise ToolException("Unsupported archive action")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
