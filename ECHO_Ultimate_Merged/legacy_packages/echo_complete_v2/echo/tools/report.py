from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from tools._base import ToolException

def report(title: str, body: str, output: str = "memory/report.md") -> str:
    """Render a simple Markdown report."""
    try:
        tpl = Template("# {{ title }}\n\n{{ body }}\n")
        out = Path(output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(tpl.render(title=title, body=body), encoding="utf-8")
        return str(out)
    except Exception as e:
        raise ToolException(str(e)) from e
