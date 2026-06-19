from __future__ import annotations

from bs4 import BeautifulSoup
from tools._shared import json_dump, http_get, strip_html, scan_links
from core.exceptions import ToolException

def web_extract(url: str, max_chars: int = 12000, **kwargs) -> str:
    """Fetch a web page and return readable text plus metadata."""
    try:
        url = url if url.startswith("http") else f"https://{url}"
        response = http_get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        title = soup.title.text.strip() if soup.title and soup.title.text else ""
        text = strip_html(response.text)
        return json_dump({
            "url": url,
            "title": title,
            "status_code": response.status_code,
            "text": text[:max_chars],
            "links": scan_links(response.text, 20),
        })
    except Exception as exc:
        raise ToolException(f"web_extract failed: {exc}")
