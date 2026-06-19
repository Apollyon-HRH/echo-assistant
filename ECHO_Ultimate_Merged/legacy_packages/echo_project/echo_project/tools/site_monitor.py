"""Website monitoring tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def site_monitor(url: str, baseline_path: str | None = None, **kwargs) -> str:
    """Monitor a page by hashing its text content."""
    try:
        import requests
        from bs4 import BeautifulSoup
        from pathlib import Path
        url = normalize_url(url)
        baseline = Path(baseline_path or (Path("memory") / f"{safe_filename(url)}.hash"))
        baseline.parent.mkdir(parents=True, exist_ok=True)
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        content = " ".join(soup.get_text(" ").split())
        current_hash = sha256_bytes(content.encode("utf-8"))
        previous = baseline.read_text(encoding="utf-8").strip() if baseline.exists() else ""
        baseline.write_text(current_hash, encoding="utf-8")
        changed = previous != current_hash and bool(previous)
        return json_dump({"url": url, "changed": changed, "hash": current_hash, "checked_at": now_iso()})
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
