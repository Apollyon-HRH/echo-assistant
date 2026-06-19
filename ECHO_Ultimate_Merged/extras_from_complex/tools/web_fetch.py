from __future__ import annotations
import requests
from bs4 import BeautifulSoup

def web_fetch(url: str) -> str:
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    return text[:20000]
