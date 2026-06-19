from __future__ import annotations

from tools._base import ToolException

def monitor() -> str:
    """Return CPU/RAM (and GPU if available) stats."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory().percent
        gpu = "n/a"
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = f"{gpus[0].load*100:.1f}%"
        except Exception:
            pass
        return f"cpu={cpu:.1f}%; ram={ram:.1f}%; gpu={gpu}"
    except Exception as e:
        raise ToolException(str(e)) from e
