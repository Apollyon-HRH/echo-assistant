from __future__ import annotations

import subprocess

from tools._base import ToolException

def terminal(command: str, confirm: bool = True) -> str:
    """Run a shell command."""
    try:
        if confirm:
            answer = input(f"Run command? {command} [y/N]: ").strip().lower()
            if answer not in {"y", "yes"}:
                return "Cancelled."
        proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        return (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    except subprocess.TimeoutExpired as e:
        raise ToolException("Terminal command timeout") from e
    except Exception as e:
        raise ToolException(str(e)) from e
