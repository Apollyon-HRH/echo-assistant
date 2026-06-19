"""Headless browsing tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def browser(url: str, action: str = "open", selector: str | None = None, **kwargs) -> str:
    """Use Playwright for headless browsing."""
    try:
        from pathlib import Path
        url = normalize_url(url)
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            raise ToolException(f"Playwright unavailable: {exc}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)
            if action == "screenshot":
                path = kwargs.get("path") or str(Path("temp") / "browser.png")
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=path, full_page=True)
                browser.close()
                return path
            if action == "click" and selector:
                page.click(selector)
            html = page.content()
            text = page.inner_text("body")
            browser.close()
            return text if action in {"open", "text"} else html
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
