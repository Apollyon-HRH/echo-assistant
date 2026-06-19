"""Windows toast notification tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def toast(title: str, message: str, **kwargs) -> str:
    """Show a Windows toast notification."""
    try:
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5)
            return "Toast enviado"
        except Exception as exc:
            raise ToolException(f"Toast unavailable: {exc}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
