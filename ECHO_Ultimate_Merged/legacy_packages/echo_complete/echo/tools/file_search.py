import re
from pathlib import Path

from core.exceptions import ToolException

def file_search(path: str, pattern: str, content: bool = False, recursive: bool = True, regex: bool = False) -> str:
    """Search files by name or content recursively."""
    try:
        root = Path(path)
        if not root.exists():
            raise ToolException(f"Caminho não encontrado: {root}")
        matches = []
        globber = root.rglob("*") if recursive else root.glob("*")
        compiled = re.compile(pattern) if regex else None
        for file in globber:
            if not file.is_file():
                continue
            target = file.read_text(encoding="utf-8", errors="ignore") if content else file.name
            ok = bool(compiled.search(target)) if compiled else (pattern.lower() in target.lower())
            if ok:
                matches.append(str(file))
        return "\n".join(matches) or "Nenhuma correspondência."
    except Exception as e:
        raise ToolException(f"Erro na ferramenta file_search: {e}") from e
