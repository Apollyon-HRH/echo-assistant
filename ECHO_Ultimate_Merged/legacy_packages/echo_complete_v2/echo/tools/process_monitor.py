from __future__ import annotations

from tools._base import ToolException

def process_monitor(action: str = "list", pid: int | None = None) -> str:
    """List or manage processes."""
    try:
        import psutil
        if action == "list":
            out = []
            for p in psutil.process_iter(["pid", "name", "status"]):
                out.append(f"{p.info['pid']} {p.info['name']} {p.info['status']}")
            return "\n".join(out[:200])
        if action == "kill" and pid:
            psutil.Process(pid).terminate()
            return "terminated"
        return "Unsupported action"
    except Exception as e:
        raise ToolException(str(e)) from e
