from datetime import datetime, timedelta
from pathlib import Path

from core.exceptions import ToolException

def cleanup(path: str = "temp", days: int = 7) -> str:
    """Delete files older than N days in a directory."""
    try:
        root = Path(path)
        if not root.exists():
            return "Diretório não encontrado."
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0
        for f in root.rglob("*"):
            if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                f.unlink()
                removed += 1
        return f"{removed} arquivo(s) removido(s)"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta cleanup: {e}") from e
