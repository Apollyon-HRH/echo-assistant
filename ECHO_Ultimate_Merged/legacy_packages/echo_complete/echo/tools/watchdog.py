import json
import time
from pathlib import Path

from core.exceptions import ToolException
from tools._shared import file_hash

STATE_FILE = Path("memory/watchdog_state.json")

def watchdog(path: str, duration: int = 10) -> str:
    """Poll a directory and report changes over a short interval."""
    try:
        root = Path(path)
        if not root.exists():
            raise ToolException(f"Caminho não encontrado: {root}")
        def snapshot() -> dict[str, str]:
            data = {}
            for f in root.rglob("*"):
                if f.is_file():
                    data[str(f)] = file_hash(f, "sha256")
            return data
        before = snapshot()
        time.sleep(max(1, duration))
        after = snapshot()
        added = [p for p in after if p not in before]
        removed = [p for p in before if p not in after]
        changed = [p for p in after if p in before and before[p] != after[p]]
        return json.dumps({"added": added, "removed": removed, "changed": changed}, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta watchdog: {e}") from e
