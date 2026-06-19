from __future__ import annotations

from tools._base import ToolException
from tools.common import http_head

def link_checker(url: str, timeout: int = 15) -> str:
    """Check whether a link responds successfully."""
    try:
        resp = http_head(url, timeout=timeout)
        return f"{url} -> {resp.status_code}"
    except Exception as e:
        raise ToolException(str(e)) from e
