"""Text classifier tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def classifier(text: str, labels: str = "", **kwargs) -> str:
    """Classify text into simple heuristic labels."""
    try:
        label_list = [x.strip() for x in labels.split(",") if x.strip()]
        lower = text.lower()
        if not label_list:
            label_list = ["tech", "general", "question", "code"]
        scored = []
        for label in label_list:
            score = sum(1 for w in label.lower().split() if w in lower) + (1 if label.lower() in lower else 0)
            scored.append((score, label))
        scored.sort(reverse=True)
        return json_dump({"label": scored[0][1], "scores": scored})
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
