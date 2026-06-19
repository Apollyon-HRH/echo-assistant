import json
from pathlib import Path

from core.exceptions import ToolException

STATE_FILE = Path("memory/cron_jobs.json")

def cron(action: str = "add", name: str = "", schedule: str = "", command: str = "") -> str:
    """Manage simple scheduled jobs stored in JSON."""
    try:
        jobs = []
        if STATE_FILE.exists():
            jobs = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if action == "list":
            return json.dumps(jobs, ensure_ascii=False, indent=2)
        if action == "add":
            jobs.append({"name": name, "schedule": schedule, "command": command})
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATE_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
            return f"Job adicionado: {name}"
        if action == "remove":
            jobs = [j for j in jobs if j.get("name") != name]
            STATE_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
            return f"Job removido: {name}"
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta cron: {e}") from e
