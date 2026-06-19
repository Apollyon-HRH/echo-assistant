from __future__ import annotations

from pathlib import Path
from io import BytesIO

import requests
from bs4 import BeautifulSoup

from tools._base import ToolException

def web_extract(url: str) -> str:
    """
    Extract readable text from HTML or PDF.
    """
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "").lower()
        if "pdf" in content_type or url.lower().endswith(".pdf"):
            try:
                import pdfplumber
                text = []
                with pdfplumber.open(BytesIO(resp.content)) as pdf:
                    for page in pdf.pages:
                        text.append(page.extract_text() or "")
                return "\n".join(text).strip()
            except Exception as e:
                raise ToolException(f"PDF extraction failed: {e}") from e
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text("\n", strip=True)
        return text[:40000]
    except Exception as e:
        raise ToolException(f"web_extract failed: {e}") from e
