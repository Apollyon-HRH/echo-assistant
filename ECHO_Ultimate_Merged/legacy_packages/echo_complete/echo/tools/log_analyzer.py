import re
from pathlib import Path

from core.exceptions import ToolException

def log_analyzer(path: str, patterns: str = "error,fail,warning") -> str:
    """Search log files for selected patterns."""
    try:
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="ignore")
        pats = [x.strip() for x in patterns.split(",") if x.strip()]
        hits = []
        for pat in pats:
            count = len(re.findall(pat, text, flags=re.I))
            hits.append(f"{pat}: {count}")
        return "\n".join(hits)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta log_analyzer: {e}") from e
