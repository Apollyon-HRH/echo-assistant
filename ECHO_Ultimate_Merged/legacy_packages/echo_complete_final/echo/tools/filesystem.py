from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.exceptions import ToolException
from ._shared import read_text, write_text, read_json, write_json, read_yaml, write_yaml, read_csv, write_csv

def filesystem(path: str, content: str | None = None, mode: str = "auto") -> str:
    """Read or write files across common formats."""
    p = Path(path).expanduser()
    mode = mode.lower()
    if content is None:
        if not p.exists():
            raise ToolException(f"File not found: {p}")
        suffix = p.suffix.lower()
        if mode == "json" or suffix == ".json":
            return json.dumps(read_json(p), ensure_ascii=False, indent=2)
        if mode in {"yaml", "yml"} or suffix in {".yaml", ".yml"}:
            import yaml
            return yaml.safe_dump(read_yaml(p), allow_unicode=True, sort_keys=False)
        if mode == "csv" or suffix == ".csv":
            return json.dumps(read_csv(p), ensure_ascii=False, indent=2)
        return read_text(p)

    suffix = p.suffix.lower()
    if mode == "json" or suffix == ".json":
        return write_json(p, json.loads(content))
    if mode in {"yaml", "yml"} or suffix in {".yaml", ".yml"}:
        import yaml
        obj = yaml.safe_load(content)
        return write_yaml(p, obj)
    if mode == "csv" or suffix == ".csv":
        obj = json.loads(content)
        if not isinstance(obj, list):
            raise ToolException("CSV write expects a JSON list of objects in content")
        return write_csv(p, obj)
    return write_text(p, content)
