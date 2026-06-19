from __future__ import annotations

from pathlib import Path
import zipfile

from core.exceptions import ToolException
from ._shared import ensure_parent

def backup(source: str, destination: str | None = None) -> str:
    """Create a zip backup of a file or directory."""
    src = Path(source).expanduser()
    if not src.exists():
        raise ToolException(f"Source not found: {src}")
    dest = Path(destination).expanduser() if destination else src.with_suffix(".backup.zip")
    ensure_parent(dest)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        if src.is_dir():
            for p in src.rglob("*"):
                zf.write(p, p.relative_to(src.parent))
        else:
            zf.write(src, src.name)
    return str(dest)
