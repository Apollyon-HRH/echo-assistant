from __future__ import annotations

import shutil
import tarfile
import zipfile
from pathlib import Path

from core.exceptions import ToolException

def archive(path: str, action: str = "zip", output: str | None = None) -> str:
    """Compress or extract zip/tar/gz archives."""
    p = Path(path).expanduser()
    action = action.lower()
    out = Path(output).expanduser() if output else None

    if action in {"zip", "tar", "gz"}:
        if not out:
            out = p.with_suffix(".zip" if action == "zip" else ".tar.gz")
        out.parent.mkdir(parents=True, exist_ok=True)
        if action == "zip":
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
                if p.is_dir():
                    for item in p.rglob("*"):
                        zf.write(item, item.relative_to(p.parent))
                else:
                    zf.write(p, p.name)
        else:
            with tarfile.open(out, "w:gz") as tf:
                tf.add(p, arcname=p.name)
        return str(out)

    if action == "extract":
        if not out:
            out = p.with_name(p.stem + "_extracted")
        out.mkdir(parents=True, exist_ok=True)
        if zipfile.is_zipfile(p):
            with zipfile.ZipFile(p) as zf:
                zf.extractall(out)
        elif tarfile.is_tarfile(p):
            with tarfile.open(p) as tf:
                tf.extractall(out)
        else:
            raise ToolException(f"Unsupported archive: {p}")
        return str(out)

    raise ToolException(f"Unsupported action: {action}")
