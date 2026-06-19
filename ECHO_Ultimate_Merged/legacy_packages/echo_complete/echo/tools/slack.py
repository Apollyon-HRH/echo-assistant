import os

import requests

from core.exceptions import ToolException

def slack(text: str, webhook_url: str = "") -> str:
    """Send a message through a Slack webhook."""
    try:
        url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        if not url:
            raise ToolException("SLACK_WEBHOOK_URL não configurada")
        resp = requests.post(url, json={"text": text}, timeout=30)
        resp.raise_for_status()
        return "Mensagem enviada ao Slack"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta slack: {e}") from e
