from __future__ import annotations
from pathlib import Path
import json
import yaml

def convert(path: str, target: str) -> str:
    p = Path(path)
    data = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        obj = json.loads(data)
    elif p.suffix.lower() in [".yaml", ".yml"]:
        obj = yaml.safe_load(data)
    else:
        obj = {"text": data}
    dst = p.with_suffix(f".{target}")
    if target == "json":
        dst.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    elif target in ("yaml", "yml"):
        dst.write_text(yaml.safe_dump(obj, allow_unicode=True), encoding="utf-8")
    else:
        dst.write_text(str(obj), encoding="utf-8")
    return str(dst)
