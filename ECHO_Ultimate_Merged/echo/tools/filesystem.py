from __future__ import annotations

from pathlib import Path
import shutil
from tools._shared import json_dump, read_text_file, write_text_file
from core.exceptions import ToolException

def filesystem(action: str, path: str, content: str | None = None, dest: str | None = None, **kwargs) -> str:
    """Basic filesystem actions: read, write, delete, copy, move."""
    try:
        p = Path(path)
        if action == "read":
            return json_dump({"path": path, "content": read_text_file(p)})
        if action == "write":
            if content is None:
                raise ToolException("content is required for write")
            return json_dump({"path": write_text_file(p, content)})
        if action == "delete":
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink(missing_ok=True)
            return json_dump({"deleted": str(p)})
        if action in {"copy", "move"}:
            if not dest:
                raise ToolException("dest is required for copy/move")
            dst = Path(dest)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if action == "copy":
                shutil.copy2(p, dst)
            else:
                shutil.move(str(p), str(dst))
            return json_dump({"source": str(p), "dest": str(dst), "action": action})
        raise ToolException(f"Unknown action: {action}")
    except Exception as exc:
        raise ToolException(f"filesystem failed: {exc}")
