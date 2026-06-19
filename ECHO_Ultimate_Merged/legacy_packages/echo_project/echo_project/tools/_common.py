"""Shared helpers for ECHO tools."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from urllib.parse import urlparse

import requests

from core.exceptions import ToolException


def ensure_parent(path: Path) -> None:
    """Ensure a parent directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def json_dump(data: Any) -> str:
    """Serialize data to formatted JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def safe_filename(name: str) -> str:
    """Create a filesystem-safe file name."""
    name = re.sub(r"[^\w\-. ]+", "_", name, flags=re.UNICODE)
    return name.strip("._ ") or "file"


def sha256_bytes(data: bytes) -> str:
    """Hash bytes using SHA-256."""
    return hashlib.sha256(data).hexdigest()


def read_text_file(path: Path, encoding: str = "utf-8") -> str:
    """Read a text file safely."""
    return path.read_text(encoding=encoding, errors="replace")


def write_text_file(path: Path, content: str, encoding: str = "utf-8") -> str:
    """Write a text file and return the path."""
    ensure_parent(path)
    path.write_text(content, encoding=encoding)
    return str(path)


def download_stream(url: str, dest: Path, timeout: int = 60) -> str:
    """Download a file with streaming and return the destination path."""
    ensure_parent(dest)
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        written = 0
        with dest.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                handle.write(chunk)
                written += len(chunk)
    return str(dest)


def run_subprocess(command: str, timeout: int = 120, shell: bool = True) -> Tuple[int, str, str]:
    """Run a subprocess and return code/stdout/stderr."""
    completed = subprocess.run(
        command,
        shell=shell,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return completed.returncode, completed.stdout, completed.stderr


def normalize_url(url: str) -> str:
    """Normalize a URL with a default scheme if needed."""
    parsed = urlparse(url)
    if not parsed.scheme:
        return "https://" + url
    return url


def now_iso() -> str:
    """Return current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"
