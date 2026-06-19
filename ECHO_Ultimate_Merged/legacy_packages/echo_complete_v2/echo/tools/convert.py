from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from tools._base import ToolException

def convert(path: str, output: str, target: str) -> str:
    """Convert between CSV, JSON, YAML, and XML for simple tabular data."""
    try:
        src = Path(path)
        data = None
        suffix = src.suffix.lower()
        if suffix == ".csv":
            with src.open(newline="", encoding="utf-8", errors="ignore") as f:
                data = list(csv.DictReader(f))
        elif suffix == ".json":
            data = json.loads(src.read_text(encoding="utf-8"))
        elif suffix in {".yml", ".yaml"}:
            data = yaml.safe_load(src.read_text(encoding="utf-8"))
        else:
            data = src.read_text(encoding="utf-8", errors="ignore")
        out = Path(output)
        out.parent.mkdir(parents=True, exist_ok=True)
        target = target.lower()
        if target == "json":
            out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        elif target in {"yaml", "yml"}:
            out.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        elif target == "csv":
            if isinstance(data, list) and data and isinstance(data[0], dict):
                with out.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                    writer.writeheader()
                    writer.writerows(data)
            else:
                raise ToolException("CSV conversion needs list of dicts")
        else:
            out.write_text(str(data), encoding="utf-8")
        return str(out)
    except Exception as e:
        raise ToolException(str(e)) from e
