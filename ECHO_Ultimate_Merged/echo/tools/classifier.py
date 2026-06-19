from __future__ import annotations

from tools._shared import json_dump
from core.exceptions import ToolException

def classifier(text: str, labels: list[str] | None = None, **kwargs) -> str:
    """Assign a simple rule-based label."""
    try:
        labels = labels or ["general", "code", "research", "task"]
        t = text.lower()
        if any(k in t for k in ["def ", "class ", "import ", "xml", "json", "yaml", "regex", "sql"]):
            label = next((x for x in labels if x in {"code", "task"}), labels[0])
        elif any(k in t for k in ["pesquisa", "research", "estudo", "fonte", "referência"]):
            label = next((x for x in labels if x in {"research", "general"}), labels[0])
        else:
            label = labels[0]
        return json_dump({"label": label, "labels": labels})
    except Exception as exc:
        raise ToolException(f"classifier failed: {exc}")
