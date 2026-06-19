from pathlib import Path

from core.exceptions import ToolException
from tools._shared import file_hash

def hash(path: str, algorithm: str = "sha256") -> str:
    """Compute a file hash."""
    try:
        return file_hash(Path(path), algorithm)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta hash: {e}") from e
