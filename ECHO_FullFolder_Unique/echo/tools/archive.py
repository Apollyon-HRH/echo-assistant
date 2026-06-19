from __future__ import annotations

from pathlib import Path
import zipfile
from tools._shared import json_dump
from core.exceptions import ToolException

def archive(action: str, source: str, dest: str | None = None, **kwargs) -> str:
    """Create, extract or inspect ZIP archives."""
    try:
        src = Path(source)
        if action == "list":
            with zipfile.ZipFile(src) as zf:
                return json_dump({"members": zf.namelist()})
        if action == "extract":
            if not dest:
                raise ToolException("dest is required for extract")
            target = Path(dest)
            target.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(src) as zf:
                zf.extractall(target)
            return json_dump({"extracted_to": str(target)})
        if action == "create":
            if not dest:
                raise ToolException("dest is required for create")
            out = Path(dest)
            with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for file in src.rglob("*"):
                    if file.is_file():
                        zf.write(file, arcname=file.relative_to(src))
            return json_dump({"archive": str(out)})
        raise ToolException(f"Unknown action: {action}")
    except Exception as exc:
        raise ToolException(f"archive failed: {exc}")
