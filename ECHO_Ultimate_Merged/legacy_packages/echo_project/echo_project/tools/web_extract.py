"""Web extraction tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def web_extract(url: str, **kwargs) -> str:
    """Extract readable text from HTML or PDF."""
    try:
        import requests
        from bs4 import BeautifulSoup
        url = normalize_url(url)
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        if "pdf" in content_type or url.lower().endswith(".pdf"):
            import io
            import pdfplumber
            text_parts = []
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts).strip()
        soup = BeautifulSoup(response.text, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
        return text
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
