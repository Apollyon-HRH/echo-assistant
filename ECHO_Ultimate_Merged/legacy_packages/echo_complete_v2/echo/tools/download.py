from __future__ import annotations
from pathlib import Path

from tools._base import ToolException
from tools._utils import download_file

def download(url: str, dest: str | None = None, timeout: int = 60) -> str:
    """Download a file with progress display."""
    try:
        return download_file(url, dest=dest, timeout=timeout)
    except Exception as e:
        raise ToolException(str(e)) from e
