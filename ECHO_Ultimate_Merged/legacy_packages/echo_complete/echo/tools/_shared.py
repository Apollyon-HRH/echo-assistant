
"""Shared helpers for ECHO tools."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import tarfile
import tempfile
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

from core.exceptions import ToolException

ROOT = Path(__file__).resolve().parent.parent
TEMP_DIR = ROOT / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def ensure_parent(path: Path) -> None:
    """Ensure the parent directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def read_text(path: str | Path, encoding: str = "utf-8") -> str:
    """Read a text file safely."""
    p = Path(path)
    return p.read_text(encoding=encoding, errors="replace")


def write_text(path: str | Path, content: str, encoding: str = "utf-8") -> Path:
    """Write text content to a file."""
    p = Path(path)
    ensure_parent(p)
    p.write_text(content, encoding=encoding)
    return p


def file_hash(path: str | Path, algorithm: str = "sha256") -> str:
    """Return the hash of a file."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_read(path: str | Path) -> Any:
    """Read JSON from disk."""
    return json.loads(read_text(path))


def json_write(path: str | Path, data: Any) -> Path:
    """Write JSON to disk."""
    return write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


def yaml_read(path: str | Path) -> Any:
    """Read YAML from disk."""
    import yaml
    return yaml.safe_load(read_text(path))


def yaml_write(path: str | Path, data: Any) -> Path:
    """Write YAML to disk."""
    import yaml
    return write_text(path, yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def xml_escape(text: str) -> str:
    """Escape text for XML output."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )


def text_from_response(resp: requests.Response, limit: int = 20000) -> str:
    """Return readable text from a requests response."""
    ctype = resp.headers.get("content-type", "")
    if "application/json" in ctype:
        return json.dumps(resp.json(), ensure_ascii=False, indent=2)
    text = resp.text
    return text[:limit]


def safe_filename(name: str) -> str:
    """Convert a string to a safe filename."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "file"


def ensure_dir(path: str | Path) -> Path:
    """Create directory if missing and return it."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def now_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def parse_bool(value: Any) -> bool:
    """Interpret a value as boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def timeout_run(command: str, timeout: int = 30, shell: bool = True) -> subprocess.CompletedProcess:
    """Execute a command with a timeout."""
    return subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=timeout)


def format_kv(items: Dict[str, Any]) -> str:
    """Format key-value pairs as aligned lines."""
    return "\n".join(f"{k}: {v}" for k, v in items.items())


def jsonl_append(path: str | Path, item: Dict[str, Any]) -> Path:
    """Append an item to a JSONL file."""
    p = Path(path)
    ensure_parent(p)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    return p


def collect_files(root: str | Path, recursive: bool = True) -> List[Path]:
    """Collect files under a directory."""
    p = Path(root)
    pattern = "**/*" if recursive else "*"
    return [f for f in p.glob(pattern) if f.is_file()]
