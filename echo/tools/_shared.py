
from __future__ import annotations

import csv
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

from core.exceptions import ToolException

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def json_dump(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)

def safe_filename(name: str) -> str:
    name = re.sub(r"[^\w\-. ]+", "_", name, flags=re.UNICODE)
    return name.strip("._ ") or "file"

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_text_file(path: Path, encoding: str = "utf-8") -> str:
    return path.read_text(encoding=encoding, errors="replace")

def write_text_file(path: Path, content: str, encoding: str = "utf-8") -> str:
    ensure_parent(path)
    path.write_text(content, encoding=encoding)
    return str(path)

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        return "https://" + url
    return url

def http_get(url: str, timeout: int = 30, headers: Optional[Dict[str, str]] = None) -> requests.Response:
    return requests.get(url, timeout=timeout, headers=headers or {"User-Agent": "ECHO/3.0"})

def http_post(url: str, json_body: Any = None, timeout: int = 30, headers: Optional[Dict[str, str]] = None) -> requests.Response:
    return requests.post(url, json=json_body, timeout=timeout, headers=headers or {"User-Agent": "ECHO/3.0"})

def download_stream(url: str, dest: Path, timeout: int = 60) -> str:
    ensure_parent(dest)
    with requests.get(url, stream=True, timeout=timeout, headers={"User-Agent": "ECHO/3.0"}) as response:
        response.raise_for_status()
        with dest.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    handle.write(chunk)
    return str(dest)

def run_subprocess(command: str, timeout: int = 120, shell: bool = True, cwd: str | None = None) -> Tuple[int, str, str]:
    completed = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    return completed.returncode, completed.stdout, completed.stderr

def split_chunks(text: str, max_len: int = 3900) -> List[str]:
    if len(text) <= max_len:
        return [text]
    chunks: List[str] = []
    current: List[str] = []
    size = 0
    for paragraph in text.split("\n\n"):
        paragraph_size = len(paragraph) + 2
        if current and size + paragraph_size > max_len:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            size = paragraph_size
        else:
            current.append(paragraph)
            size += paragraph_size
    if current:
        chunks.append("\n\n".join(current))
    return chunks

def scan_links(html: str, limit: int = 20) -> List[str]:
    return re.findall(r'href=["\\\'](.*?)["\\\']', html, flags=re.IGNORECASE)[:limit]

def strip_html(html: str) -> str:
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()

def zip_folder(folder: Path, out_path: Path) -> str:
    ensure_parent(out_path)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in folder.rglob("*"):
            if file.is_file():
                zf.write(file, arcname=file.relative_to(folder))
    return str(out_path)

def unzip_file(zip_path: Path, dest: Path) -> str:
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    return str(dest)

def file_type(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"

def size_of(path: Path) -> int:
    return path.stat().st_size
