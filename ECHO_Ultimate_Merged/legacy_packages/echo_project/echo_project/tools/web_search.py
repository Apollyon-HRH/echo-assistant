"""Web search tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def web_search(query: str, num_results: int = 3, **kwargs) -> str:
    """Search the web using DuckDuckGo with fallback to Google."""
    try:
        results = []
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for item in ddgs.text(query, max_results=num_results):
                    results.append({
                        "title": item.get("title"),
                        "href": item.get("href"),
                        "body": item.get("body"),
                    })
        except Exception:
            try:
                from googlesearch import search as google_search
                for url in google_search(query, num_results=num_results):
                    results.append({"title": url, "href": url, "body": ""})
            except Exception as exc:
                raise ToolException(f"Web search failed: {exc}")
        return json_dump(results[:num_results])
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
