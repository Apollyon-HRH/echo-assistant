from __future__ import annotations

from typing import Iterable, List

import requests

from core.exceptions import ToolException
from ._shared import json_pretty

def link_checker(urls: str | list[str], timeout: int = 15) -> str:
    """Check whether URLs respond successfully using HEAD/GET fallback."""
    if isinstance(urls, str):
        url_list = [u.strip() for u in urls.splitlines() if u.strip()]
        if not url_list and urls.strip():
            url_list = [urls.strip()]
    else:
        url_list = urls

    if not url_list:
        raise ToolException("No URLs provided")

    results = []
    for url in url_list:
        status = None
        error = None
        try:
            r = requests.head(url, allow_redirects=True, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
            status = r.status_code
            if status >= 400:
                r = requests.get(url, allow_redirects=True, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
                status = r.status_code
        except Exception as exc:
            error = str(exc)
        results.append({"url": url, "status": status, "ok": bool(status and status < 400), "error": error})
    return json_pretty(results)
