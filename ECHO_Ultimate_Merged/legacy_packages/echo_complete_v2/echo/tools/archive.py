from __future__ import annotations

from pathlib import Path

from tools._base import ToolException
from tools.common import extract_zip, make_zip, extract_tar, make_tar

def archive(src: str, dest: str, action: str = "zip") -> str:
    """Compress or extract archives."""
    try:
        if action == "zip":
            return make_zip(src, dest)
        if action == "unzip":
            return extract_zip(src, dest)
        if action == "tar":
            return make_tar(src, dest)
        if action == "untar":
            return extract_tar(src, dest)
        raise ToolException("Unsupported archive action")
    except Exception as e:
        raise ToolException(str(e)) from e
