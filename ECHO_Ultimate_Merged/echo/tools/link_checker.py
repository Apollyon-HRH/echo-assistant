from __future__ import annotations

from tools._shared import json_dump, http_get
from core.exceptions import ToolException

def link_checker(urls: list[str], **kwargs) -> str:
    """Check HTTP status and latency for multiple URLs."""
    try:
        out = []
        for url in urls:
            if not url.startswith("http"):
                url = "https://" + url
            try:
                r = http_get(url, timeout=20)
                out.append({"url": url, "status_code": r.status_code, "ok": r.ok})
            except Exception as exc:
                out.append({"url": url, "error": str(exc), "ok": False})
        return json_dump(out)
    except Exception as exc:
        raise ToolException(f"link_checker failed: {exc}")
