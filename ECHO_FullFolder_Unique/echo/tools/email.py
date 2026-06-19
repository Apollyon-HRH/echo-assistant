from __future__ import annotations

import smtplib
from email.message import EmailMessage

from core.config import CONFIG
from core.exceptions import ToolException
from tools._shared import json_dump

def email(to: str, subject: str, body: str, **kwargs) -> str:
    """Send an email through SMTP credentials from config/env."""
    try:
        env = CONFIG.get("env", {})
        server = env.get("smtp_server")
        if not server:
            raise ToolException("SMTP_SERVER is not configured")
        msg = EmailMessage()
        msg["From"] = env.get("smtp_user", "")
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(server, int(env.get("smtp_port", 587)), timeout=30) as smtp:
            smtp.starttls()
            if env.get("smtp_user"):
                smtp.login(env.get("smtp_user"), env.get("smtp_password", ""))
            smtp.send_message(msg)
        return json_dump({"sent": True, "to": to, "subject": subject})
    except Exception as exc:
        raise ToolException(f"email failed: {exc}")
