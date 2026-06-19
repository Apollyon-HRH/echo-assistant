from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import List

from core.exceptions import ToolException

def watchdog(path: str, duration: int = 15) -> str:
    """Monitor a folder for file changes for a short duration."""
    watch_path = Path(path).expanduser()
    if not watch_path.exists():
        raise ToolException(f"Path not found: {watch_path}")

    try:
        from watchdog.observers import Observer  # type: ignore
        from watchdog.events import FileSystemEventHandler  # type: ignore
    except Exception:
        # fallback polling
        snapshot = {p: p.stat().st_mtime for p in watch_path.rglob("*") if p.is_file()}
        time.sleep(min(duration, 5))
        changes = []
        for p in watch_path.rglob("*"):
            if p.is_file():
                old = snapshot.get(p)
                cur = p.stat().st_mtime
                if old is None:
                    changes.append(f"created: {p}")
                elif old != cur:
                    changes.append(f"modified: {p}")
        return "\n".join(changes) or "No changes detected"

    events: List[str] = []
    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            events.append(f"created: {event.src_path}")
        def on_modified(self, event):
            events.append(f"modified: {event.src_path}")
        def on_deleted(self, event):
            events.append(f"deleted: {event.src_path}")
    observer = Observer()
    observer.schedule(Handler(), str(watch_path), recursive=True)
    observer.start()
    try:
        time.sleep(duration)
    finally:
        observer.stop()
        observer.join()
    return "\n".join(events) or "No changes detected"
