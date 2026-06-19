"""SMTP email tool."""

from __future__ import annotations

import json
import os
import smtplib
from pathlib import Path

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def email(to: str, subject: str, body: str, attachments: list[str] | None = None, **kwargs) -> str:
    """Send email via SMTP."""
    try:
        import os
        import smtplib
        from email.message import EmailMessage
        attachments = attachments or []
        server = os.getenv("SMTP_SERVER", "")
        port = int(os.getenv("SMTP_PORT", "587"))
        user = os.getenv("SMTP_USER", "")
        password = os.getenv("SMTP_PASSWORD", "")
        if not all([server, user, password]):
            raise ToolException("SMTP configuration is incomplete")
        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        for file_path in attachments:
            p = Path(file_path)
            if p.exists():
                msg.add_attachment(p.read_bytes(), maintype="application", subtype="octet-stream", filename=p.name)
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        return "E-mail enviado com sucesso"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
