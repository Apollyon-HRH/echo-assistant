"""Archive creation and extraction."""

from __future__ import annotations
from pathlib import Path
import shutil
import zipfile

from tools._common import ToolException, ensure_parent

def archive(path: str, action: str = "zip", output: str | None = None) -> str:
    """Zip or unzip files and folders."""
    p = Path(path).expanduser()
    try:
        if action == "zip":
            out = Path(output) if output else p.with_suffix(".zip")
            ensure_parent(out)
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
                if p.is_dir():
                    for item in p.rglob("*"):
                        zf.write(item, item.relative_to(p.parent))
                else:
                    zf.write(p, p.name)
            return str(out)
        if action == "unzip":
            out = Path(output) if output else p.with_suffix("")
            out.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(p, "r") as zf:
                zf.extractall(out)
            return str(out)
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Falha no archive: {e}")
