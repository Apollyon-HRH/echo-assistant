from __future__ import annotations

import json
from pathlib import Path

from core.exceptions import ToolException
from ._shared import read_json, write_json, read_yaml, write_yaml, read_csv, write_csv, read_text, write_text

def convert(input_path: str, output_path: str, input_format: str = "auto", output_format: str = "auto") -> str:
    """Convert between JSON, YAML, CSV and plain text."""
    inp = Path(input_path).expanduser()
    out = Path(output_path).expanduser()
    if not inp.exists():
        raise ToolException(f"Input not found: {inp}")

    if input_format == "auto":
        input_format = inp.suffix.lstrip(".").lower() or "txt"
    if output_format == "auto":
        output_format = out.suffix.lstrip(".").lower() or "txt"

    if input_format == "json":
        data = read_json(inp)
    elif input_format in {"yaml", "yml"}:
        data = read_yaml(inp)
    elif input_format == "csv":
        data = read_csv(inp)
    else:
        data = read_text(inp)

    if output_format == "json":
        return write_json(out, data)
    if output_format in {"yaml", "yml"}:
        return write_yaml(out, data)
    if output_format == "csv":
        if not isinstance(data, list):
            raise ToolException("CSV output expects list of dicts")
        return write_csv(out, data)
    return write_text(out, data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2))
