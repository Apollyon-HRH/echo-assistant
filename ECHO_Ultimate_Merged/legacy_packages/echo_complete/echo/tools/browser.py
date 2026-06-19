
from pathlib import Path

from core.exceptions import ToolException


def browser(url: str, action: str = "open", selector: str = "", text: str = "", screenshot_path: str = "") -> str:
    """Browse a page headlessly and optionally click or capture content."""
    try:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                if action == "click" and selector:
                    page.click(selector)
                if action == "type" and selector:
                    page.fill(selector, text)
                if action == "screenshot":
                    path = screenshot_path or "temp/browser.png"
                    Path(path).parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=path, full_page=True)
                    result = f"Screenshot salvo em {path}"
                else:
                    result = f"Título: {page.title()}\nURL: {page.url}\n\n{(page.text_content('body') or '')[:8000]}"
                browser.close()
                return result
        except Exception:
            import requests
            from bs4 import BeautifulSoup
            resp = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.text.strip() if soup.title and soup.title.text else ""
            return f"Título: {title}\nURL: {url}\n\n{' '.join(soup.get_text(' ').split())[:8000]}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta browser: {e}") from e
