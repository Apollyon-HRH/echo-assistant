import os

from core.exceptions import ToolException

def telegram(chat_id: str, text: str, parse_mode: str = "Markdown") -> str:
    """Send a Telegram message using the bot token."""
    try:
        token = os.getenv("TELEGRAM_TOKEN")
        if not token:
            raise ToolException("TELEGRAM_TOKEN não configurado")
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode}, timeout=30)
        resp.raise_for_status()
        return "Mensagem enviada ao Telegram"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta telegram: {e}") from e
