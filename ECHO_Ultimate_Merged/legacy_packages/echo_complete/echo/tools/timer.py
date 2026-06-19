import threading
from pathlib import Path

from core.exceptions import ToolException
from tools._shared import ensure_dir

def timer(seconds: int, message: str = "Timer concluído") -> str:
    """Start a simple background timer."""
    try:
        def _done():
            print(f"\n[TIMER] {message}")
        t = threading.Timer(seconds, _done)
        t.daemon = True
        t.start()
        return f"Timer iniciado por {seconds} segundos"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta timer: {e}") from e
