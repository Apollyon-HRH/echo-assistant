from __future__ import annotations

import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, List

from core.config import CONFIG
from core.exceptions import ToolException

def email(to: str, subject: str, body: str, attachments: list[str] | None = None) -> str:
    """Send email through SMTP with optional attachments."""
    env = CONFIG.get("env", {})
    server = env.get("smtp_server")
    port = int(env.get("smtp_port", 587))
    user = env.get("smtp_user")
    password = env.get("smtp_password")
    if not all([server, user, password]):
        raise ToolException("SMTP configuration missing in .env")

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    for item in attachments or []:
        p = Path(item).expanduser()
        if not p.exists():
            raise ToolException(f"Attachment not found: {p}")
        mime, _ = mimetypes.guess_type(str(p))
        maintype, subtype = (mime.split("/", 1) if mime else ("application", "octet-stream"))
        msg.add_attachment(p.read_bytes(), maintype=maintype, subtype=subtype, filename=p.name)

    try:
        with smtplib.SMTP(server, port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
    except Exception as exc:
        raise ToolException(f"Email send failed: {exc}") from exc
    return "Email sent successfully"
