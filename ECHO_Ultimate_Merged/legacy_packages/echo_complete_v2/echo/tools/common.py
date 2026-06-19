from __future__ import annotations

import csv
import json
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import Any

import requests

from tools._base import ToolException
from tools._utils import TEMP, ensure_parent, write_text

def http_get(url: str, timeout: int = 30, headers: dict | None = None) -> requests.Response:
    try:
        resp = requests.get(url, timeout=timeout, headers=headers or {}, allow_redirects=True)
        resp.raise_for_status()
        return resp
    except Exception as e:
        raise ToolException(str(e)) from e

def http_head(url: str, timeout: int = 15, headers: dict | None = None) -> requests.Response:
    try:
        resp = requests.head(url, timeout=timeout, headers=headers or {}, allow_redirects=True)
        resp.raise_for_status()
        return resp
    except Exception as e:
        raise ToolException(str(e)) from e

def run_command(command: str, shell: bool = True, timeout: int = 120) -> str:
    try:
        proc = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=timeout)
        return (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    except subprocess.TimeoutExpired as e:
        raise ToolException("command timeout") from e
    except Exception as e:
        raise ToolException(str(e)) from e

def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)

def read_csv(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        return list(csv.DictReader(f))

def write_csv(path: str | Path, rows: list[dict]) -> str:
    if not rows:
        return write_text(path, "")
    path = ensure_parent(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return str(path)

def extract_zip(src: str | Path, dest: str | Path) -> str:
    try:
        with zipfile.ZipFile(src) as z:
            z.extractall(dest)
        return str(dest)
    except Exception as e:
        raise ToolException(str(e)) from e

def make_zip(src: str | Path, dest: str | Path) -> str:
    try:
        src = Path(src)
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
            if src.is_dir():
                for p in src.rglob("*"):
                    if p.is_file():
                        z.write(p, p.relative_to(src))
            else:
                z.write(src, src.name)
        return str(dest)
    except Exception as e:
        raise ToolException(str(e)) from e

def extract_tar(src: str | Path, dest: str | Path) -> str:
    try:
        with tarfile.open(src) as t:
            t.extractall(dest)
        return str(dest)
    except Exception as e:
        raise ToolException(str(e)) from e

def make_tar(src: str | Path, dest: str | Path) -> str:
    try:
        src = Path(src)
        with tarfile.open(dest, "w:gz") as t:
            t.add(src, arcname=src.name)
        return str(dest)
    except Exception as e:
        raise ToolException(str(e)) from e
