from __future__ import annotations

from tools._shared import json_dump
from core.exceptions import ToolException

def monitor(**kwargs) -> str:
    """Return a compact machine health snapshot."""
    try:
        import psutil, platform
        return json_dump({
            "platform": platform.platform(),
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent if hasattr(psutil, "disk_usage") else None,
        })
    except Exception as exc:
        raise ToolException(f"monitor failed: {exc}")
