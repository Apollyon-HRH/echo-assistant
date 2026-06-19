"""Convert data between common formats."""

from __future__ import annotations

from pathlib import Path
import csv
import json
import xml.etree.ElementTree as ET

import yaml

from tools._common import ensure_parent, ToolException


def csv_to_json(csv_path: str, json_path: str) -> str:
    """Convert CSV to JSON."""
    in_path = Path(csv_path)
    out_path = Path(json_path)
    ensure_parent(out_path)
    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out_path)


def json_to_csv(json_path: str, csv_path: str) -> str:
    """Convert JSON list of objects to CSV."""
    in_path = Path(json_path)
    out_path = Path(csv_path)
    ensure_parent(out_path)
    data = json.loads(in_path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ToolException("JSON deve ser uma lista de objetos.")
    keys = sorted({k for row in data if isinstance(row, dict) for k in row.keys()})
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    return str(out_path)


def yaml_to_json(yaml_path: str, json_path: str) -> str:
    """Convert YAML to JSON."""
    in_path = Path(yaml_path)
    out_path = Path(json_path)
    ensure_parent(out_path)
    data = yaml.safe_load(in_path.read_text(encoding="utf-8"))
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out_path)


def json_to_yaml(json_path: str, yaml_path: str) -> str:
    """Convert JSON to YAML."""
    in_path = Path(json_path)
    out_path = Path(yaml_path)
    ensure_parent(out_path)
    data = json.loads(in_path.read_text(encoding="utf-8"))
    out_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return str(out_path)


def xml_to_json(xml_path: str, json_path: str) -> str:
    """Convert XML to a JSON representation."""
    in_path = Path(xml_path)
    out_path = Path(json_path)
    ensure_parent(out_path)
    tree = ET.parse(in_path)
    root = tree.getroot()

    def walk(node):
        return {
            "tag": node.tag,
            "attrib": node.attrib,
            "text": (node.text or "").strip(),
            "children": [walk(child) for child in node],
        }

    out_path.write_text(json.dumps(walk(root), ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out_path)


def json_to_xml(json_path: str, xml_path: str, root_tag: str = "root") -> str:
    """Convert JSON to XML."""
    in_path = Path(json_path)
    out_path = Path(xml_path)
    ensure_parent(out_path)
    data = json.loads(in_path.read_text(encoding="utf-8"))

    def build(parent, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                child = ET.SubElement(parent, str(k))
                build(child, v)
        elif isinstance(obj, list):
            for item in obj:
                child = ET.SubElement(parent, "item")
                build(child, item)
        else:
            parent.text = "" if obj is None else str(obj)

    root = ET.Element(root_tag)
    build(root, data)
    ET.ElementTree(root).write(out_path, encoding="utf-8", xml_declaration=True)
    return str(out_path)
