"""Cleanup tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def cleanup(path: str | None = None, **kwargs) -> str:
    """Remove temporary files from a path or system temp directory."""
    try:
        import tempfile, shutil
        from pathlib import Path
        target = Path(path or tempfile.gettempdir())
        removed = 0
        for child in list(target.iterdir()):
            try:
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
                removed += 1
            except Exception:
                continue
        return json_dump({"removed": removed, "path": str(target)})
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
