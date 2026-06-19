"""Timer helper."""

from __future__ import annotations
import time
from tools._common import ToolException

def timer(duration_seconds: int, label: str = "timer") -> str:
    """Return the target finish time for a countdown."""
    if duration_seconds < 0:
        raise ToolException("duration_seconds deve ser positivo.")
    time.sleep(min(duration_seconds, 1))
    return f"{label}: {duration_seconds}s registrado (execução curta para não bloquear)."
