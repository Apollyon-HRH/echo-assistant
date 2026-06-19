"""Simple browser-like fetch and parse helper."""

from __future__ import annotations

from bs4 import BeautifulSoup
import requests

from tools._common import ToolException, clamp_text


def browser(url: str) -> str:
    """Open a page and return title, text, and links."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        links = []
        for a in soup.find_all("a", href=True)[:15]:
            links.append(f"{a.get_text(' ', strip=True)[:60]} -> {a['href']}")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text("\n", strip=True)
        return clamp_text(
            f"TITLE: {title}\n\nTEXT:\n{text}\n\nLINKS:\n" + "\n".join(links),
            12000,
        )
    except Exception as e:
        raise ToolException(f"Falha no browser: {e}")
