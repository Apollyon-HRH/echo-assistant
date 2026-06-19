from __future__ import annotations

import time
from pathlib import Path

import psutil

from core.exceptions import ToolException
from ._shared import json_pretty

def monitor(duration: int = 5) -> str:
    """Monitor CPU and memory usage over a time window."""
    if duration <= 0:
        raise ToolException("duration must be > 0")
    samples = []
    for _ in range(duration):
        samples.append({
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
        })
    return json_pretty({"samples": samples})
