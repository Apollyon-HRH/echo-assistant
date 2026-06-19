from core.exceptions import ToolException

def ner(text: str) -> str:
    """Extract named entities using spaCy if available."""
    try:
        import spacy
        try:
            nlp = spacy.load("pt_core_news_sm")
        except Exception:
            nlp = spacy.blank("pt")
        doc = nlp(text)
        ents = []
        for ent in getattr(doc, "ents", []):
            ents.append(f"{ent.text} [{ent.label_}]")
        return "\n".join(ents) or "Nenhuma entidade encontrada."
    except Exception as e:
        raise ToolException(f"Erro na ferramenta ner: {e}") from e
