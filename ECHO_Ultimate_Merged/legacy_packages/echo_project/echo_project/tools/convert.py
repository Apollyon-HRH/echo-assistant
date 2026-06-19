"""Format conversion tool."""

from __future__ import annotations

import json
from pathlib import Path

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def convert(path: str, to: str, output_path: str | None = None, **kwargs) -> str:
    """Convert between CSV, JSON, YAML, and XML when possible."""
    try:
        from pathlib import Path
        import csv, json
        p = Path(path)
        data = p.read_text(encoding="utf-8")
        src_ext = p.suffix.lower()
        dest = Path(output_path or p.with_suffix(f".{to.lower()}"))
        if src_ext == ".csv" and to.lower() == "json":
            rows = list(csv.DictReader(data.splitlines()))
            dest.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
            return str(dest)
        if src_ext == ".json" and to.lower() == "csv":
            rows = json.loads(data)
            if not rows:
                dest.write_text("", encoding="utf-8")
            else:
                import csv
                with dest.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(rows)
            return str(dest)
        if src_ext in {".yaml", ".yml"} and to.lower() == "json":
            import yaml
            obj = yaml.safe_load(data)
            dest.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
            return str(dest)
        if src_ext == ".json" and to.lower() in {"yaml", "yml"}:
            import yaml
            obj = json.loads(data)
            dest.write_text(yaml.safe_dump(obj, allow_unicode=True, sort_keys=False), encoding="utf-8")
            return str(dest)
        if src_ext == ".json" and to.lower() == "xml":
            import xml.etree.ElementTree as ET
            obj = json.loads(data)
            root = ET.Element("root")
            def append(parent, item, key="item"):
                if isinstance(item, dict):
                    node = ET.SubElement(parent, key)
                    for k, v in item.items():
                        append(node, v, k)
                elif isinstance(item, list):
                    for v in item:
                        append(parent, v, key)
                else:
                    parent.text = str(item)
            append(root, obj, "item")
            dest.write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
            return str(dest)
        return "Conversão não suportada para esta combinação"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
