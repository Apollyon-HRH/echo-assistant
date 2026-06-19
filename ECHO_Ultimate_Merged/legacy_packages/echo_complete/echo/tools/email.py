import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from core.exceptions import ToolException

def email(to: str, subject: str, body: str, attachments: str = "") -> str:
    """Send an email using SMTP settings from environment variables."""
    try:
        server = os.getenv("SMTP_SERVER")
        port = int(os.getenv("SMTP_PORT", "587"))
        user = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASSWORD")
        if not all([server, user, password]):
            raise ToolException("SMTP_SERVER, SMTP_USER e SMTP_PASSWORD precisam estar definidos")
        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        for item in [x.strip() for x in attachments.split(",") if x.strip()]:
            path = Path(item)
            if path.exists() and path.is_file():
                data = path.read_bytes()
                msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=path.name)
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        return f"E-mail enviado para {to}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta email: {e}") from e
