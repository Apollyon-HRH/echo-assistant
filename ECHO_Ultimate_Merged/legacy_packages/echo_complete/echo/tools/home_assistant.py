import os

import requests

from core.exceptions import ToolException

def home_assistant(action: str, entity_id: str = "", state: str = "", service: str = "") -> str:
    """Call the Home Assistant REST API."""
    try:
        base = os.getenv("HOME_ASSISTANT_URL", "")
        token = os.getenv("HOME_ASSISTANT_TOKEN", "")
        if not base or not token:
            raise ToolException("HOME_ASSISTANT_URL/HOME_ASSISTANT_TOKEN não configurados")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        if action == "state":
            resp = requests.get(f"{base}/api/states/{entity_id}", headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.text
        if action == "call" and service and entity_id:
            domain, svc = service.split(".", 1) if "." in service else (service, "toggle")
            resp = requests.post(f"{base}/api/services/{domain}/{svc}", headers=headers, json={"entity_id": entity_id}, timeout=30)
            resp.raise_for_status()
            return "Serviço executado"
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta home_assistant: {e}") from e
