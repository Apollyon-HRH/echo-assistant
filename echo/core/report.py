
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

def build_session_report(session_id: str, turns: List[Dict[str, Any]], summary: str = "") -> str:
    lines = [f"# Relatório da sessão: {session_id}", ""]
    if summary:
        lines += ["## Resumo", summary, ""]
    lines += ["## Turnos", ""]
    for i, turn in enumerate(turns, 1):
        role = turn.get("role", "user")
        content = str(turn.get("content", "")).strip()
        lines.append(f"{i}. **{role}**: {content[:500]}")
    return "\n".join(lines)

def export_report(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return str(p)
