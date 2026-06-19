from __future__ import annotations

from pathlib import Path

from tools._base import ToolException
from tools.common import make_zip
from tools._utils import now_stamp

def backup(source: str, dest_dir: str = "memory/backups") -> str:
    """Create a timestamped ZIP backup."""
    try:
        d = Path(dest_dir)
        d.mkdir(parents=True, exist_ok=True)
        out = d / f"backup_{now_stamp()}.zip"
        return make_zip(source, out)
    except Exception as e:
        raise ToolException(str(e)) from e
