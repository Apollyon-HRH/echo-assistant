from __future__ import annotations

from pathlib import Path
from datetime import datetime
from tools._shared import json_dump, http_get, safe_filename
from core.exceptions import ToolException

def site_monitor(url: str, snapshot_dir: str = "./memory/site_snapshots", **kwargs) -> str:
    """Capture a page snapshot for future diffing."""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        path = Path(snapshot_dir)
        path.mkdir(parents=True, exist_ok=True)
        html = http_get(url, timeout=30).text
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file = path / f"{safe_filename(url)}_{stamp}.html"
        file.write_text(html, encoding="utf-8")
        return json_dump({"url": url, "snapshot": str(file), "bytes": len(html)})
    except Exception as exc:
        raise ToolException(f"site_monitor failed: {exc}")
