import json

from core.exceptions import ToolException

def process_monitor(action: str = "list", pid: int = 0, name: str = "") -> str:
    """List or manage processes using psutil."""
    try:
        import psutil
        if action == "list":
            rows = []
            for p in psutil.process_iter(["pid", "name", "username"]):
                rows.append(f"{p.info['pid']} | {p.info.get('name','')} | {p.info.get('username','')}")
            return "\n".join(rows[:200])
        if action == "kill" and pid:
            psutil.Process(pid).terminate()
            return f"Processo {pid} terminado"
        if action == "find" and name:
            matches = []
            for p in psutil.process_iter(["pid", "name"]):
                if name.lower() in (p.info.get("name") or "").lower():
                    matches.append(f"{p.info['pid']} | {p.info['name']}")
            return "\n".join(matches) or "Nenhuma correspondência."
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta process_monitor: {e}") from e
