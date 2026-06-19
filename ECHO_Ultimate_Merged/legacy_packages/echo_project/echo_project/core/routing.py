"""Model routing rules for ECHO."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Route = Literal["geral_pesado", "geral_leve", "codigo_pesado", "codigo_leve", "manual"]


CODE_KEYWORDS = {
    "código", "funcão", "função", "script", "debug", "algoritmo", "parser",
    "compilador", "injetar", "exploit", "buffer", "overflow", "reverse",
    "engenharia reversa", "assembly", "ponteiro", "malloc", "fork", "thread",
    "socket", "payload", "shellcode",
}
GENERAL_HEAVY_KEYWORDS = {
    "explique", "detalhe", "teoria", "história", "filosofia", "por que",
    "como funciona", "significado",
}


def route_prompt(prompt: str, manual_mode: str = "auto") -> str:
    """Return the model key to use for a prompt."""
    manual_mode = (manual_mode or "auto").lower()
    if manual_mode in {"gp", "gl", "cp", "cl"}:
        return {"gp": "geral_pesado", "gl": "geral_leve", "cp": "codigo_pesado", "cl": "codigo_leve"}[manual_mode]

    normalized = prompt.lower().strip()
    words = [w for w in normalized.replace("\n", " ").split(" ") if w]
    word_count = len(words)

    if any(keyword in normalized for keyword in CODE_KEYWORDS):
        return "codigo_pesado" if word_count >= 10 else "codigo_leve"

    if any(keyword in normalized for keyword in GENERAL_HEAVY_KEYWORDS):
        return "geral_pesado"

    if word_count > 30:
        return "geral_pesado"

    return "geral_leve"


def manual_alias(mode: str) -> str:
    """Normalize a manual routing alias."""
    mapping = {"gp": "geral_pesado", "gl": "geral_leve", "cp": "codigo_pesado", "cl": "codigo_leve", "auto": "auto"}
    return mapping.get(mode.lower(), "auto")
