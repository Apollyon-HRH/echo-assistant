"""Directory operations."""

from __future__ import annotations
from pathlib import Path
import shutil

from tools._common import ToolException


def _tree(path: Path, prefix: str = "", depth: int = 2) -> list[str]:
    entries = []
    if depth < 0:
        return entries
    try:
        items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except Exception:
        return [f"{prefix}{path}"]
    for i, item in enumerate(items):
        connector = "└── " if i == len(items) - 1 else "├── "
        entries.append(f"{prefix}{connector}{item.name}")
        if item.is_dir() and depth > 0:
            extension = "    " if i == len(items) - 1 else "│   "
            entries.extend(_tree(item, prefix + extension, depth - 1))
    return entries


def directory(path: str, action: str = "list", target: str | None = None) -> str:
    """List or manipulate directories."""
    p = Path(path).expanduser()
    try:
        if action == "list":
            return "\n".join(_tree(p))
        if action == "mkdir":
            p.mkdir(parents=True, exist_ok=True)
            return f"Diretório criado: {p}"
        if action == "delete":
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            return f"Removido: {p}"
        if action == "copy":
            if not target:
                raise ToolException("target é obrigatório para copy")
            dest = Path(target).expanduser()
            if p.is_dir():
                shutil.copytree(p, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(p, dest)
            return f"Copiado para {dest}"
        if action == "move":
            if not target:
                raise ToolException("target é obrigatório para move")
            dest = Path(target).expanduser()
            shutil.move(str(p), str(dest))
            return f"Movido para {dest}"
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Falha em directory: {e}")
