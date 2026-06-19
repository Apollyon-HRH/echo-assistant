from __future__ import annotations

import threading
import time

from tools._base import ToolException

def timer(seconds: int, message: str = "Timer done") -> str:
    """Start a delayed notifier in a background thread."""
    try:
        def _job():
            time.sleep(seconds)
            print(message)
        threading.Thread(target=_job, daemon=True).start()
        return f"Timer started for {seconds}s"
    except Exception as e:
        raise ToolException(str(e)) from e
