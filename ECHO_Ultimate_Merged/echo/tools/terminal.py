from __future__ import annotations

from tools._shared import json_dump, run_subprocess
from core.exceptions import ToolException

def terminal(command: str, timeout: int = 120, cwd: str | None = None, **kwargs) -> str:
    """Run a shell command with captured output."""
    try:
        code, out, err = run_subprocess(command, timeout=timeout, cwd=cwd)
        return json_dump({"returncode": code, "stdout": out, "stderr": err})
    except Exception as exc:
        raise ToolException(f"terminal failed: {exc}")
