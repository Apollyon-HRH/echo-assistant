from __future__ import annotations

from pathlib import Path
from tools._shared import json_dump
from core.exceptions import ToolException
from core.report import build_session_report, export_report

def report(session_id: str, turns_path: str, out: str = "./temp/report.md", **kwargs) -> str:
    """Render a markdown report from a session JSON file."""
    try:
        import json
        data = json.loads(Path(turns_path).read_text(encoding="utf-8"))
        report_text = build_session_report(session_id, data.get("turns", []), data.get("summary", ""))
        return json_dump({"report": export_report(out, report_text)})
    except Exception as exc:
        raise ToolException(f"report failed: {exc}")
