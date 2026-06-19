from __future__ import annotations

from bs4 import BeautifulSoup
from tools._shared import json_dump, http_get, scan_links
from core.exceptions import ToolException

def browser(url: str, **kwargs) -> str:
    """Open a page and return a compact browser-like snapshot."""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        response = http_get(url, timeout=30)
        soup = BeautifulSoup(response.text, "lxml")
        title = soup.title.text.strip() if soup.title and soup.title.text else ""
        h1 = [h.get_text(" ", strip=True) for h in soup.find_all("h1")[:5]]
        links = scan_links(response.text, 25)
        return json_dump({
            "url": url,
            "status_code": response.status_code,
            "title": title,
            "headings": h1,
            "links": links,
        })
    except Exception as exc:
        raise ToolException(f"browser failed: {exc}")
