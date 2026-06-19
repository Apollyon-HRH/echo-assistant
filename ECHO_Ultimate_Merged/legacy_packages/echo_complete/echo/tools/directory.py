import shutil
from pathlib import Path

from core.exceptions import ToolException

def directory(path: str, action: str = "list", destination: str = "") -> str:
    """List, copy, move, or delete files and directories."""
    try:
        p = Path(path)
        if action == "list":
            if not p.exists():
                raise ToolException(f"Caminho não encontrado: {p}")
            items = []
            for child in sorted(p.iterdir()):
                suffix = "/" if child.is_dir() else ""
                items.append(f"{child.name}{suffix}")
            return "\n".join(items) or "(vazio)"
        if action == "copy":
            d = Path(destination)
            if p.is_dir():
                shutil.copytree(p, d, dirs_exist_ok=True)
            else:
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, d)
            return f"Copiado para {d}"
        if action == "move":
            d = Path(destination)
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(d))
            return f"Movido para {d}"
        if action == "delete":
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink(missing_ok=True)
            return f"Removido: {p}"
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta directory: {e}") from e
