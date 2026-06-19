from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from tools._base import ToolException

def email(to: str, subject: str, body: str, attachments: list[str] | None = None) -> str:
    """Send e-mail via SMTP."""
    server = os.getenv("SMTP_SERVER", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    if not all([server, user, password]):
        raise ToolException("SMTP variables are missing in .env")
    try:
        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        for ap in attachments or []:
            p = Path(ap)
            msg.add_attachment(p.read_bytes(), maintype="application", subtype="octet-stream", filename=p.name)
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        return "Email sent."
    except Exception as e:
        raise ToolException(str(e)) from e
