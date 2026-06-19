"""Terminal execution tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def terminal(command: str, confirm: bool = True, timeout: int = 120, **kwargs) -> str:
    """Execute a shell command with optional confirmation."""
    try:
        if confirm:
            answer = input(f"Confirmar execução do comando? [y/N] {command}\n> ").strip().lower()
            if answer not in {"y", "yes", "s", "sim"}:
                return "Execução cancelada pelo usuário"
        code, stdout, stderr = run_subprocess(command, timeout=timeout, shell=True)
        return json_dump({"returncode": code, "stdout": stdout, "stderr": stderr})
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
