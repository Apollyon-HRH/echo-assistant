from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List

from core.exceptions import ToolException
from ._shared import json_pretty, human_size

def directory(path: str, action: str = "list", target: str | None = None) -> str:
    """List, create, copy, move, rename or delete directories/files."""
    p = Path(path).expanduser()
    action = action.lower().strip()

    if action == "list":
        if not p.exists():
            raise ToolException(f"Path not found: {p}")
        entries = []
        for item in sorted(p.iterdir()):
            entries.append({
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "size": human_size(item.stat().st_size) if item.is_file() else "",
            })
        return json_pretty(entries)

    if action == "mkdir":
        p.mkdir(parents=True, exist_ok=True)
        return str(p)

    if action == "delete":
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
        return f"Deleted {p}"

    if action in {"copy", "move", "rename"}:
        if not target:
            raise ToolException("target is required for copy/move/rename")
        dest = Path(target).expanduser()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if action == "copy":
            if p.is_dir():
                shutil.copytree(p, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(p, dest)
        else:
            shutil.move(str(p), str(dest))
        return f"{action.title()} completed: {p} -> {dest}"

    raise ToolException(f"Unsupported action: {action}")
