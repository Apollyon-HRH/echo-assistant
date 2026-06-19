"""Telegram Bot API helper."""

from __future__ import annotations
import os
import requests

from tools._common import ToolException

def telegram(action: str, chat_id: str | None = None, text: str | None = None) -> str:
    """Perform a minimal Telegram API action."""
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    if not token:
        raise ToolException("TELEGRAM_TOKEN ausente.")
    base = f"https://api.telegram.org/bot{token}"
    try:
        if action == "me":
            r = requests.get(f"{base}/getMe", timeout=30)
            r.raise_for_status()
            return r.text
        if action == "send":
            if not chat_id or text is None:
                raise ToolException("chat_id e text são obrigatórios para send.")
            r = requests.post(f"{base}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=30)
            r.raise_for_status()
            return r.text
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Falha no telegram tool: {e}")
