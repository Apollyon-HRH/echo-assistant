"""Run shell commands."""

from __future__ import annotations
import subprocess
import sys

from tools._common import ToolException

def terminal(command: str, confirm: bool = True, timeout: int = 120) -> str:
    """Execute a shell command with optional confirmation."""
    if confirm:
        answer = input(f"Executar comando? {command}\n[y/N]: ").strip().lower()
        if answer not in {"y", "yes", "s", "sim"}:
            return "Comando cancelado."
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        output = (result.stdout or "") + (result.stderr or "")
        return f"EXIT={result.returncode}\n{output}".strip()
    except subprocess.TimeoutExpired:
        raise ToolException("Ferramenta cancelada por timeout")
    except Exception as e:
        raise ToolException(f"Falha no terminal: {e}")
