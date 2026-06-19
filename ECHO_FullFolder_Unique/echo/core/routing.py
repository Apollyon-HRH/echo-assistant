
from __future__ import annotations

CODE_KEYWORDS = {
    "código", "codigo", "função", "funcao", "script", "algoritmo", "debug", "python",
    "xml", "regex", "parser", "compilador", "terminal", "api", "json", "yaml", "sql",
    "refatorar", "otimizar", "stack", "heap", "thread", "socket", "classe", "objeto",
    "javascript", "typescript", "bash", "docker", "pipeline",
}
HEAVY_KEYWORDS = {
    "explique", "detalhado", "complexo", "profundo", "arquitetura", "comparar",
    "análise", "analise", "raciocínio", "raciocinio", "longo", "passo a passo",
    "implementação", "implementacao",
}

def manual_alias(mode: str) -> str:
    return {
        "gp": "geral_pesado",
        "gl": "geral_leve",
        "cp": "codigo_pesado",
        "cl": "codigo_leve",
        "auto": "auto",
    }.get(mode.lower(), "auto")

def route_prompt(prompt: str, manual_mode: str = "auto") -> str:
    manual_mode = manual_alias(manual_mode)
    if manual_mode != "auto":
        return manual_mode
    normalized = (prompt or "").lower().strip()
    words = [w for w in normalized.replace("\n", " ").split(" ") if w]
    score = 0
    if any(k in normalized for k in CODE_KEYWORDS):
        score += 2
    if any(k in normalized for k in HEAVY_KEYWORDS):
        score += 1
    if len(words) > 45:
        score += 1
    if any(ch in normalized for ch in ["{", "}", "(", ")", ";", "->", "==", "import ", "def "]):
        score += 1
    if score >= 3:
        return "codigo_pesado"
    if score == 2:
        return "codigo_leve"
    if score == 1:
        return "geral_pesado"
    return "geral_leve"
