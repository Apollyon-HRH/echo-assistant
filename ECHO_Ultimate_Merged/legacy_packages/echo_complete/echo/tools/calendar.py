import os
from pathlib import Path

from core.exceptions import ToolException
from tools._shared import ensure_dir, safe_filename

def calendar(action: str, title: str = "", start: str = "", end: str = "", description: str = "") -> str:
    """Create calendar entries or export them as ICS files."""
    try:
        if action == "ics":
            out = Path("temp") / f"{safe_filename(title)}.ics"
            ensure_dir(out.parent)
            content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{title}
DTSTART:{start}
DTEND:{end}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR
"""
            out.write_text(content, encoding="utf-8")
            return f"Arquivo ICS criado em {out}"
        if action == "google":
            creds = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "")
            if not creds:
                raise ToolException("GOOGLE_CALENDAR_CREDENTIALS não configurado")
            return f"Integração Google Calendar depende de credenciais em {creds}"
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta calendar: {e}") from e
