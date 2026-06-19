from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import threading
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import requests
from requests import Response, Session

from core.exceptions import ToolException
from core.config import CONFIG

ROOT = Path(CONFIG["runtime"]["root"]).resolve()
TEMP_DIR = Path(CONFIG["runtime"]["temp_path"]).resolve()
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def as_path(value: str | os.PathLike[str]) -> Path:
    return Path(value).expanduser().resolve()

def session() -> Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "ECHO/1.0 (+local assistant)"})
    return s

def read_text(path: Path, encoding: str = "utf-8") -> str:
    return path.read_text(encoding=encoding)

def write_text(path: Path, content: str, encoding: str = "utf-8") -> str:
    ensure_parent(path)
    path.write_text(content, encoding=encoding)
    return str(path)

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, data: Any) -> str:
    ensure_parent(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)

def read_yaml(path: Path) -> Any:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def write_yaml(path: Path, data: Any) -> str:
    import yaml
    ensure_parent(path)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return str(path)

def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> str:
    ensure_parent(path)
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return str(path)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return str(path)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_text(data: str) -> str:
    return sha256_bytes(data.encode("utf-8"))

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def human_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f}{unit}" if unit != "B" else f"{n}{unit}"
        n /= 1024
    return f"{n:.1f}PB"

def list_files_recursive(root: Path, pattern: str = "*") -> List[Path]:
    return [p for p in root.rglob(pattern) if p.is_file()]

def run_command(command: str, timeout: int = 60, shell: bool = True, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command if shell else command.split(),
        shell=shell,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )

def download_to_path(url: str, dest: Path, timeout: int = 60, chunk_size: int = 1024 * 64) -> str:
    ensure_parent(dest)
    s = session()
    with s.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", "0"))
        downloaded = 0
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
    return str(dest)

def zip_folder(source: Path, destination: Path) -> str:
    ensure_parent(destination)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in source.rglob("*"):
            zf.write(path, path.relative_to(source.parent))
    return str(destination)

def extract_archive(path: Path, destination: Path) -> str:
    ensure_parent(destination / "x")
    destination.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            zf.extractall(destination)
    elif tarfile.is_tarfile(path):
        with tarfile.open(path) as tf:
            tf.extractall(destination)
    else:
        raise ToolException(f"Unsupported archive format: {path}")
    return str(destination)

def safe_delete(path: Path) -> str:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
    return f"Deleted: {path}"

def json_pretty(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)

def split_chunks(text: str, limit: int = 3500) -> List[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    for i in range(0, len(text), limit):
        chunks.append(text[i:i+limit])
    return chunks

def which(program: str) -> str | None:
    return shutil.which(program)

def now_ts() -> float:
    return time.time()

def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def tail_text(path: Path, lines: int = 100) -> str:
    data = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(data[-lines:])

def first_existing(paths: Iterable[Path]) -> Optional[Path]:
    for p in paths:
        if p.exists():
            return p
    return None

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def json_loads_maybe(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return None

def timeit(func):
    from functools import wraps
    import time as _time
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = _time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = _time.perf_counter() - start
        return result, elapsed
    return wrapper
