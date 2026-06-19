from __future__ import annotations

from pathlib import Path
from datetime import datetime
from tools._shared import json_dump, zip_folder
from core.exceptions import ToolException

def backup(source: str, dest_dir: str = "./memory/backups", **kwargs) -> str:
    """Create a timestamped backup ZIP."""
    try:
        src = Path(source)
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out = dest / f"{src.name}_{stamp}.zip"
        zip_folder(src, out)
        return json_dump({"backup": str(out)})
    except Exception as exc:
        raise ToolException(f"backup failed: {exc}")
