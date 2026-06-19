from __future__ import annotations

from pathlib import Path
from datetime import datetime

from core.exceptions import ToolException
from ._shared import ensure_parent

def report(title: str, content: str, output_path: str | None = None) -> str:
    """Generate a markdown report file."""
    if not title.strip() or not content.strip():
        raise ToolException("title and content cannot be empty")
    out = Path(output_path).expanduser() if output_path else Path.cwd() / f"{title.lower().replace(' ', '_')}.md"
    ensure_parent(out)
    md = f"# {title}\n\nGenerated: {datetime.now().isoformat()}\n\n{content}\n"
    out.write_text(md, encoding="utf-8")
    return str(out)
