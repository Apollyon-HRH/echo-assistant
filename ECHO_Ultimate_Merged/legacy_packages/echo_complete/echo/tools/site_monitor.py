import json
from pathlib import Path

import requests

from core.exceptions import ToolException
from tools._shared import file_hash, ensure_dir

STATE_FILE = Path("memory/site_monitor.json")

def site_monitor(url: str, state_name: str = "") -> str:
    """Monitor a site's content hash and report changes."""
    try:
        ensure_dir(STATE_FILE.parent)
        state = {}
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        resp = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        content = resp.text
        h = file_hash(Path(__file__), "sha256") if False else __import__("hashlib").sha256(content.encode("utf-8", errors="ignore")).hexdigest()
        key = state_name or url
        previous = state.get(key, {}).get("hash")
        state[key] = {"url": url, "hash": h}
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        if previous and previous != h:
            return f"Alteração detectada em {url}"
        if previous == h:
            return f"Sem alterações em {url}"
        return f"Monitor iniciado para {url}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta site_monitor: {e}") from e
