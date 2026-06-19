"""Report generation tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def report(title: str, content: str, output_path: str | None = None, format: str = "md", **kwargs) -> str:
    """Generate a Markdown or HTML report."""
    try:
        from pathlib import Path
        from jinja2 import Template
        out = Path(output_path or f"{safe_filename(title)}.{ 'html' if format.lower() == 'html' else 'md' }")
        out.parent.mkdir(parents=True, exist_ok=True)
        if format.lower() == "html":
            template = Template("<html><head><meta charset='utf-8'><title>{{ title }}</title></head><body><h1>{{ title }}</h1><pre>{{ content }}</pre></body></html>")
            out.write_text(template.render(title=title, content=content), encoding="utf-8")
        else:
            out.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")
        return str(out)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
