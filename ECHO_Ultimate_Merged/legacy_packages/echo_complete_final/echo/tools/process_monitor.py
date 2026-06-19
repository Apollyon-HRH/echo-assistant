from __future__ import annotations

import psutil

from core.exceptions import ToolException
from ._shared import json_pretty

def process_monitor(top: int = 10) -> str:
    """Return system and top-process usage stats."""
    try:
        info = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent if hasattr(psutil, "disk_usage") else None,
            "processes": [],
        }
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                procs.append(p.info)
            except Exception:
                continue
        procs.sort(key=lambda x: (x.get("cpu_percent") or 0, x.get("memory_percent") or 0), reverse=True)
        info["processes"] = procs[:top]
        return json_pretty(info)
    except Exception as exc:
        raise ToolException(f"process_monitor failed: {exc}") from exc
