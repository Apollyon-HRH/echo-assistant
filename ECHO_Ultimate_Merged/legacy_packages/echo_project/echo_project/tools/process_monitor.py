"""Process monitoring tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def process_monitor(top: int = 20, **kwargs) -> str:
    """List processes by memory usage."""
    try:
        import psutil
        procs = []
        for p in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
            try:
                info = p.info
                rss = info.get("memory_info").rss if info.get("memory_info") else 0
                procs.append({
                    "pid": info.get("pid"),
                    "name": info.get("name"),
                    "rss": rss,
                    "cpu_percent": info.get("cpu_percent"),
                })
            except Exception:
                continue
        procs.sort(key=lambda x: x["rss"], reverse=True)
        return json_dump(procs[:top])
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
