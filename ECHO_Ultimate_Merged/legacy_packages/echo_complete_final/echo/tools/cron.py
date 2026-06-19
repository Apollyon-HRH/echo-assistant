from __future__ import annotations

import threading
import time
from typing import Callable, Dict, List

from core.exceptions import ToolException

_JOBS: List[dict] = []

def cron(action: str, spec: str = "", command: str = "", interval_seconds: int = 0) -> str:
    """Minimal cron-like scheduler backed by the schedule library."""
    action = action.lower().strip()
    try:
        import schedule  # type: ignore
    except Exception as exc:
        raise ToolException(f"schedule library unavailable: {exc}") from exc

    if action == "add":
        if interval_seconds <= 0:
            raise ToolException("interval_seconds must be > 0")
        def job():
            # non-executing job placeholder: user can wire external actions
            _JOBS.append({"command": command, "spec": spec, "executed_at": time.time()})
        schedule.every(interval_seconds).seconds.do(job)
        if not any(t.name == "echo-cron-runner" for t in threading.enumerate()):
            def runner():
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            t = threading.Thread(target=runner, daemon=True, name="echo-cron-runner")
            t.start()
        return f"Scheduled every {interval_seconds}s: {command}"

    if action == "list":
        return str(_JOBS)

    if action == "clear":
        schedule.clear()
        _JOBS.clear()
        return "Cron jobs cleared"

    raise ToolException(f"Unsupported action: {action}")
