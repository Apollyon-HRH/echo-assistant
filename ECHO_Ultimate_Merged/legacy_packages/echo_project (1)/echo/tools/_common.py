"""Helpers shared by ECHO tools."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import os
import re
import tempfile
from datetime import datetime


class ToolException(RuntimeError):
    """Raised when a tool operation fails."""


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = BASE_DIR / "temp"
MEMORY_DIR = BASE_DIR / "memory"
SESSIONS_DIR = BASE_DIR / "sessions"
LOGS_DIR = BASE_DIR / "logs"

for _p in (DATA_DIR, TEMP_DIR, MEMORY_DIR, SESSIONS_DIR, LOGS_DIR):
    _p.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    """Return the current timestamp in ISO-8601 format."""
    return datetime.now().isoformat(timespec="seconds")


def safe_json_load(path: Path, default: Any):
    """Load JSON from a path, returning default on failure."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def safe_json_dump(path: Path, data: Any):
    """Write JSON to a path atomically."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def ensure_parent(path: Path) -> None:
    """Create parent directories for a path."""
    path.parent.mkdir(parents=True, exist_ok=True)


def clamp_text(text: str, limit: int = 12000) -> str:
    """Clamp text to a maximum length."""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def strip_markdown(text: str) -> str:
    """Remove common markdown markers for plain-text rendering."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"[#>*_`\[\]()]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, max_chars: int = 3500):
    """Split text into chunks suitable for chat APIs."""
    text = text or ""
    for i in range(0, len(text), max_chars):
        yield text[i:i + max_chars]


def is_url(text: str) -> bool:
    """Return True if text appears to be a URL."""
    return bool(re.match(r"^https?://", text.strip(), re.I))


def guess_filename_from_url(url: str) -> str:
    """Infer a filename from a URL."""
    tail = url.split("?")[0].rstrip("/").split("/")[-1]
    return tail or "downloaded_file"
