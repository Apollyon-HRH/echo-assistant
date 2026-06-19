from __future__ import annotations

import tempfile
from pathlib import Path

import requests

from core.exceptions import ToolException
from ._shared import normalize_text

def web_extract(url: str) -> str:
    """Extract readable text from HTML or PDF URL."""
    url = url.strip()
    if not url:
        raise ToolException("url cannot be empty")

    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    except Exception as exc:
        raise ToolException(f"Failed to download content: {exc}") from exc

    ctype = r.headers.get("content-type", "").lower()
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        try:
            import pdfplumber
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
                tmp.write(r.content)
                tmp.flush()
                text_parts = []
                with pdfplumber.open(tmp.name) as pdf:
                    for page in pdf.pages:
                        text_parts.append(page.extract_text() or "")
                return normalize_text("\n".join(text_parts))
        except Exception as exc:
            raise ToolException(f"PDF extraction failed: {exc}") from exc

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text("\n", strip=True)
        return normalize_text(text)
    except Exception as exc:
        raise ToolException(f"HTML extraction failed: {exc}") from exc
