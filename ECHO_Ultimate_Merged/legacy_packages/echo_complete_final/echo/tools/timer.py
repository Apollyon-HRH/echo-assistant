from __future__ import annotations

import threading
import time

from core.exceptions import ToolException

def timer(seconds: int, message: str = "Timer finished") -> str:
    """Run a timer in the background and return immediately."""
    if seconds <= 0:
        raise ToolException("seconds must be > 0")
    def _run():
        time.sleep(seconds)
        print(message)
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return f"Timer started for {seconds} seconds"
