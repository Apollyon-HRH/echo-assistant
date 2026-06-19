"""Local file search."""

from __future__ import annotations
from pathlib import Path

from tools._common import ToolException, clamp_text


def file_search(query: str, root: str = ".", limit: int = 20) -> str:
    """Search file names and content locally."""
    q = query.lower().strip()
    base = Path(root).expanduser().resolve()
    if not q:
        raise ToolException("Query vazia.")
    hits = []
    for p in base.rglob("*"):
        if len(hits) >= limit:
            break
        if not p.is_file():
            continue
        if q in p.name.lower():
            hits.append(f"FILE: {p}")
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            lower = text.lower()
            if q in lower:
                idx = lower.find(q)
                snippet = clamp_text(text[max(0, idx - 80):idx + 220], 300)
                hits.append(f"CONTENT: {p}\n{snippet}")
        except Exception:
            pass
    return "\n".join(hits) if hits else "Nenhum arquivo encontrado."
