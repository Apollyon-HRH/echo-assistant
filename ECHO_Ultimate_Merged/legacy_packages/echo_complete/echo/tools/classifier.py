from core.exceptions import ToolException

def classifier(text: str, labels: str = "geral,tecnico,financeiro,academico") -> str:
    """Classify text using a simple keyword heuristic."""
    try:
        labels_list = [x.strip() for x in labels.split(",") if x.strip()]
        lower = text.lower()
        scores = {label: 0 for label in labels_list}
        keyword_map = {
            "tecnico": ["código", "script", "bug", "api", "json", "python", "sql"],
            "financeiro": ["dinheiro", "orçamento", "lucro", "preço", "custo", "mercado"],
            "academico": ["teoria", "pesquisa", "artigo", "universidade", "estudo"],
        }
        for label, kws in keyword_map.items():
            if label in scores:
                scores[label] += sum(1 for kw in kws if kw in lower)
        best = max(scores.items(), key=lambda kv: kv[1])[0]
        return best
    except Exception as e:
        raise ToolException(f"Erro na ferramenta classifier: {e}") from e
