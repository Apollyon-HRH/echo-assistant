
from __future__ import annotations

import csv
import json
from pathlib import Path

def json_to_pretty_text(raw: str) -> str:
    data = json.loads(raw)
    return json.dumps(data, ensure_ascii=False, indent=2)

def csv_to_text(path: str) -> str:
    p = Path(path)
    with p.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        return "\n".join(" | ".join(row) for row in reader)
