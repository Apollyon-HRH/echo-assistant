from __future__ import annotations

from pathlib import Path

from tools._base import ToolException
from tools._utils import TEMP, now_stamp

def browser(url: str, action: str = "open", selector: str | None = None) -> str:
    """
    Headless browser helper. Supports open/click/screenshot when Playwright is available.
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise ToolException("playwright is not installed") from e

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)
            if action == "screenshot":
                path = TEMP / f"browser_{now_stamp()}.png"
                page.screenshot(path=str(path), full_page=True)
                browser.close()
                return str(path)
            if action == "click" and selector:
                page.click(selector)
                content = page.content()
            else:
                content = page.content()
            browser.close()
            return content[:40000]
    except Exception as e:
        raise ToolException(f"browser failed: {e}") from e
