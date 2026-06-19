import os

import requests

from core.exceptions import ToolException

def discord(content: str, webhook_url: str = "") -> str:
    """Send a message through a Discord webhook."""
    try:
        url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "")
        if not url:
            raise ToolException("DISCORD_WEBHOOK_URL não configurada")
        resp = requests.post(url, json={"content": content}, timeout=30)
        resp.raise_for_status()
        return "Mensagem enviada ao Discord"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta discord: {e}") from e
