"""Send email via SMTP using environment variables."""

from __future__ import annotations
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from tools._common import ToolException

def email(to: str, subject: str, body: str, html: bool = False) -> str:
    """Send an email message."""
    host = os.getenv("SMTP_SERVER")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    if not all([host, user, password]):
        raise ToolException("SMTP não configurado no .env.")
    msg = MIMEMultipart("alternative") if html else MIMEMultipart()
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = subject
    part = MIMEText(body, "html" if html else "plain", "utf-8")
    msg.attach(part)
    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [to], msg.as_string())
        return f"Email enviado para {to}"
    except Exception as e:
        raise ToolException(f"Falha ao enviar email: {e}")
