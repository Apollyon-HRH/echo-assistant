from __future__ import annotations

import time
from tools._shared import json_dump
from core.exceptions import ToolException

def timer(seconds: int, **kwargs) -> str:
    """Count down and report elapsed time."""
    try:
        start = time.time()
        time.sleep(min(seconds, 30))
        return json_dump({"requested_seconds": seconds, "elapsed": round(time.time() - start, 2)})
    except Exception as exc:
        raise ToolException(f"timer failed: {exc}")
