"""Folder watcher tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def watchdog(path: str, timeout: int = 10, **kwargs) -> str:
    """Watch a folder for changes for a short interval."""
    try:
        from pathlib import Path
        import time
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except Exception as exc:
            raise ToolException(f"watchdog unavailable: {exc}")

        events = []

        class Handler(FileSystemEventHandler):
            def on_any_event(self, event):
                events.append({"event_type": event.event_type, "src_path": event.src_path})

        observer = Observer()
        observer.schedule(Handler(), str(Path(path)), recursive=True)
        observer.start()
        time.sleep(timeout)
        observer.stop()
        observer.join()
        return json_dump(events)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
