"""System monitor snapshot."""

from __future__ import annotations
import json
import psutil

from tools._common import ToolException

def monitor() -> str:
    """Return a snapshot of system resources."""
    try:
        data = {
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage("/")._asdict() if hasattr(psutil, "disk_usage") else {},
        }
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        raise ToolException(f"Falha no monitor: {e}")
