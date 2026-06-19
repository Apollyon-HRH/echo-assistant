"""Fetch and extract readable text from web pages or PDFs."""

from __future__ import annotations
from io import BytesIO

import requests
from bs4 import BeautifulSoup

from tools._common import ToolException, clamp_text


def web_extract(url: str) -> str:
    """Extract main text from an URL."""
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "").lower()
        if "pdf" in ctype or url.lower().endswith(".pdf"):
            try:
                import pdfplumber
                with pdfplumber.open(BytesIO(resp.content)) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                return clamp_text(text, 12000)
            except Exception as e:
                raise ToolException(f"Erro ao ler PDF: {e}")
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        text = soup.get_text("\n", strip=True)
        return clamp_text((title + "\n\n" + text).strip(), 12000)
    except Exception as e:
        raise ToolException(f"Falha ao extrair URL: {e}")
