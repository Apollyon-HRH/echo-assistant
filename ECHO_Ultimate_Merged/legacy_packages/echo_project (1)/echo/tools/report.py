"""Tool wrapper for report generation."""

from __future__ import annotations
import json
from pathlib import Path

from tools._common import ToolException
from core.report import generate_report

def report(data: str, output_path: str, format: str = "md") -> str:
    """Generate a report from JSON data."""
    try:
        obj = json.loads(data)
    except Exception as e:
        raise ToolException(f"JSON inválido: {e}")
    return generate_report(obj, output_path, format=format)
