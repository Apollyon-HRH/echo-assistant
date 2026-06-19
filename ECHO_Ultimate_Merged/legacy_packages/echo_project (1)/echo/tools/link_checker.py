"""Check availability of a set of links."""

from __future__ import annotations
import requests
from tools._common import ToolException


def link_checker(urls: str, timeout: int = 10) -> str:
    """Check one or more URLs. Separate with commas or newlines."""
    items = [u.strip() for u in urls.replace("\n", ",").split(",") if u.strip()]
    if not items:
        raise ToolException("Nenhuma URL informada.")
    out = []
    for url in items:
        try:
            r = requests.get(url, timeout=timeout, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
            out.append(f"{url} | {r.status_code} | {len(r.text)} chars")
        except Exception as e:
            out.append(f"{url} | ERROR | {e}")
    return "\n".join(out)
