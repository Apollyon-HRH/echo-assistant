"""Watch a directory for changes."""

from __future__ import annotations
from pathlib import Path
import time

from tools._common import ToolException


def watchdog(path: str, seconds: int = 5) -> str:
    """Watch a path for a short period and report changes."""
    p = Path(path).expanduser()
    if not p.exists():
        raise ToolException("Caminho inexistente.")
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except Exception:
        return "watchdog não instalado; monitoramento simples indisponível."

    events = []

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            events.append(f"{event.event_type}: {event.src_path}")

    observer = Observer()
    handler = Handler()
    observer.schedule(handler, str(p), recursive=True)
    observer.start()
    try:
        time.sleep(max(1, seconds))
    finally:
        observer.stop()
        observer.join()
    return "\n".join(events) if events else "Nenhuma alteração detectada."
