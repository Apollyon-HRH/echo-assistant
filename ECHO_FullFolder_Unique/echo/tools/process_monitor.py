from __future__ import annotations

from tools._shared import json_dump
from core.exceptions import ToolException

def process_monitor(**kwargs) -> str:
    """Return CPU, memory and process statistics."""
    try:
        import psutil
        p = psutil.Process()
        return json_dump({
            "pid": p.pid,
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "memory_percent": psutil.virtual_memory().percent,
            "process_memory": p.memory_info().rss,
        })
    except Exception as exc:
        raise ToolException(f"process_monitor failed: {exc}")
