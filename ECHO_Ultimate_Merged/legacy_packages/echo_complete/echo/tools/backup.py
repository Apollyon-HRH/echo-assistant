from datetime import datetime
from pathlib import Path
import zipfile

from core.exceptions import ToolException
from tools._shared import ensure_dir, safe_filename

def backup(path: str, destination: str = "memory") -> str:
    """Create a timestamped ZIP backup of a folder or file."""
    try:
        src = Path(path)
        if not src.exists():
            raise ToolException(f"Caminho não encontrado: {src}")
        dest_dir = ensure_dir(destination)
        out = dest_dir / f"{safe_filename(src.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            if src.is_dir():
                for file in src.rglob("*"):
                    if file.is_file():
                        zf.write(file, file.relative_to(src))
            else:
                zf.write(src, src.name)
        return f"Backup criado em {out}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta backup: {e}") from e
