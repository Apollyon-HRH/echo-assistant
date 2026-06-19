"""Link checking tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def link_checker(urls: str | list[str], **kwargs) -> str:
    """Check whether links respond successfully."""
    try:
        import requests
        if isinstance(urls, str):
            urls = [u.strip() for u in urls.splitlines() if u.strip()]
        report = []
        for url in urls:
            url = normalize_url(url)
            try:
                resp = requests.head(url, allow_redirects=True, timeout=30)
                report.append({"url": url, "status": resp.status_code, "ok": resp.status_code < 400})
            except Exception as exc:
                report.append({"url": url, "status": None, "ok": False, "error": str(exc)})
        return json_dump(report)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
