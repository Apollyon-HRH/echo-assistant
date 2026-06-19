from __future__ import annotations

import subprocess
from pathlib import Path

from core.exceptions import ToolException

def terminal(command: str, confirm: bool = True, cwd: str | None = None, timeout: int = 120) -> str:
    """Execute a PowerShell/CMD command with optional confirmation."""
    if not command.strip():
        raise ToolException("command cannot be empty")
    if confirm:
        try:
            answer = input(f"Execute command? {command}\n[y/N]: ").strip().lower()
        except Exception:
            answer = "n"
        if answer not in {"y", "yes", "s", "sim"}:
            return "Command cancelled by user"
    try:
        proc = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        output = (proc.stdout or "") + (proc.stderr or "")
        return output.strip() or f"Exit code: {proc.returncode}"
    except subprocess.TimeoutExpired:
        return "Ferramenta cancelada por timeout"
    except Exception as exc:
        raise ToolException(f"terminal failed: {exc}") from exc
