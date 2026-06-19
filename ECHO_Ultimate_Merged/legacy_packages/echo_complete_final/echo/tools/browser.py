from __future__ import annotations

from pathlib import Path

import requests

from core.exceptions import ToolException
from ._shared import TEMP_DIR, ensure_parent, normalize_text

def browser(url: str, action: str = "text", selector: str | None = None, output_path: str | None = None, wait_ms: int = 1500) -> str:
    """Headless browser utility using Playwright when available, requests fallback otherwise."""
    url = url.strip()
    if not url:
        raise ToolException("url cannot be empty")
    action = action.lower().strip()

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)
            if action == "click" and selector:
                page.click(selector)
                page.wait_for_timeout(wait_ms)
            if action == "screenshot":
                out = Path(output_path) if output_path else TEMP_DIR / "browser.png"
                ensure_parent(out)
                page.screenshot(path=str(out), full_page=True)
                browser.close()
                return str(out)
            if action == "html":
                html = page.content()
                browser.close()
                return html
            text = page.locator(selector).inner_text() if selector else page.text_content("body")
            browser.close()
            return normalize_text(text or "")
    except Exception:
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            if action == "screenshot":
                raise ToolException("Playwright unavailable; screenshot not supported in fallback mode")
            return normalize_text(r.text)
        except Exception as exc:
            raise ToolException(f"browser failed: {exc}") from exc
