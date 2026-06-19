from __future__ import annotations

from pathlib import Path
from tools._shared import json_dump
from core.exceptions import ToolException
from core.convert import json_to_pretty_text, csv_to_text

def convert(action: str, source: str, output: str | None = None, **kwargs) -> str:
    """Convert between basic text-based formats."""
    try:
        src = Path(source)
        if action == "json_pretty":
            return json_dump({"text": json_to_pretty_text(src.read_text(encoding="utf-8"))})
        if action == "csv_text":
            return json_dump({"text": csv_to_text(source)})
        raise ToolException(f"Unknown action: {action}")
    except Exception as exc:
        raise ToolException(f"convert failed: {exc}")
