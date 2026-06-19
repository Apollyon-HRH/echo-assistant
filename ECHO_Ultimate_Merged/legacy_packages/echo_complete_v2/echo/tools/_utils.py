from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import socket
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

from tools._base import ToolException

ROOT = Path(__file__).resolve().parents[1]
TEMP = ROOT / "temp"
TEMP.mkdir(exist_ok=True)

def as_text(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, ensure_ascii=False, indent=2)
    return str(obj)

def safe_filename(name: str, default: str = "file") -> str:
    name = re.sub(r"[^\w.\-]+", "_", name.strip())
    return name or default

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def guess_mime(path: str | Path) -> str:
    return mimetypes.guess_type(str(path))[0] or "application/octet-stream"

def ensure_parent(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def download_file(url: str, dest: str | Path | None = None, timeout: int = 60) -> str:
    try:
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            filename = dest or safe_filename(url.split("/")[-1] or "download.bin")
            out = ensure_parent(TEMP / filename)
            total = int(r.headers.get("content-length", 0))
            with open(out, "wb") as f, Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Downloading", total=total if total else None)
                for chunk in r.iter_content(chunk_size=1024 * 128):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
            return str(out)
    except Exception as e:
        raise ToolException(f"download failed: {e}") from e

def read_text_guess(path: str | Path) -> str:
    path = Path(path)
    if not path.exists():
        raise ToolException(f"file not found: {path}")
    return path.read_text(encoding="utf-8", errors="ignore")

def write_text(path: str | Path, content: str) -> str:
    path = ensure_parent(path)
    path.write_text(content, encoding="utf-8")
    return str(path)

def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    with suppress(Exception):
        with socket.create_connection((host, port), timeout=timeout):
            return True
    return False

def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
