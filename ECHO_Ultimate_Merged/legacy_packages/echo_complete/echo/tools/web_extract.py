
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from core.exceptions import ToolException


def web_extract(url: str) -> str:
    """Extract readable text from an HTML page or PDF."""
    try:
        resp = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "").lower()
        if "pdf" in ctype or url.lower().endswith(".pdf"):
            try:
                import pdfplumber
                from io import BytesIO
                text_parts = []
                with pdfplumber.open(BytesIO(resp.content)) as pdf:
                    for page in pdf.pages:
                        text_parts.append(page.extract_text() or "")
                return "\n".join(text_parts).strip()
            except Exception as exc:
                raise ToolException(f"Falha ao extrair PDF: {exc}") from exc
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
        return text.strip()
    except Exception as e:
        raise ToolException(f"Erro na ferramenta web_extract: {e}") from e
