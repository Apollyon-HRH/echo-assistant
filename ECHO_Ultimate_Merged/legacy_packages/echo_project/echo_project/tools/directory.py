"""Directory management tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def directory(path: str, action: str = "list", destination: str | None = None, **kwargs) -> str:
    """List, copy, move or delete directories/files."""
    try:
        from pathlib import Path
        import shutil
        p = Path(path)
        if action == "list":
            items = []
            for child in p.iterdir():
                items.append({"name": child.name, "is_dir": child.is_dir(), "size": child.stat().st_size if child.exists() else 0})
            return json_dump(items)
        if action == "copy" and destination:
            dest = Path(destination)
            if p.is_dir():
                shutil.copytree(p, dest, dirs_exist_ok=True)
            else:
                ensure_parent(dest)
                shutil.copy2(p, dest)
            return str(dest)
        if action == "move" and destination:
            dest = Path(destination)
            ensure_parent(dest)
            shutil.move(str(p), str(dest))
            return str(dest)
        if action == "delete":
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink(missing_ok=True)
            return f"Deleted: {p}"
        raise ToolException("Invalid action or missing destination")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
