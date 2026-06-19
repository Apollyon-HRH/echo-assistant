"""Tool wrapper for data conversion utilities."""

from __future__ import annotations
from core.convert import csv_to_json, json_to_csv, yaml_to_json, json_to_yaml, xml_to_json, json_to_xml

def convert(action: str, input_path: str, output_path: str, root_tag: str = "root") -> str:
    """Dispatch data conversion actions."""
    action = action.lower().strip()
    if action == "csv_to_json":
        return csv_to_json(input_path, output_path)
    if action == "json_to_csv":
        return json_to_csv(input_path, output_path)
    if action == "yaml_to_json":
        return yaml_to_json(input_path, output_path)
    if action == "json_to_yaml":
        return json_to_yaml(input_path, output_path)
    if action == "xml_to_json":
        return xml_to_json(input_path, output_path)
    if action == "json_to_xml":
        return json_to_xml(input_path, output_path, root_tag=root_tag)
    raise ValueError(f"Ação inválida: {action}")
