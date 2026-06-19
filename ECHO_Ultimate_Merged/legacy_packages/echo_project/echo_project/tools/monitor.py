"""System monitoring tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def monitor(**kwargs) -> str:
    """Monitor CPU, RAM, and GPU usage."""
    try:
        import psutil
        data = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
        }
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            data["gpu"] = [{"name": g.name, "load": g.load, "memoryUtil": g.memoryUtil} for g in gpus]
        except Exception:
            data["gpu"] = []
        return json_dump(data)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
