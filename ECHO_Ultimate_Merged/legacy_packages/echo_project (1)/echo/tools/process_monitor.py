"""Process and system monitor."""

from __future__ import annotations
import json
import psutil

from tools._common import ToolException

def process_monitor(limit: int = 10) -> str:
    """Return the top processes by CPU and memory."""
    try:
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            info = p.info
            procs.append(info)
        procs.sort(key=lambda x: (x.get("cpu_percent") or 0, x.get("memory_percent") or 0), reverse=True)
        return json.dumps(procs[:limit], ensure_ascii=False, indent=2)
    except Exception as e:
        raise ToolException(f"Falha no process monitor: {e}")
