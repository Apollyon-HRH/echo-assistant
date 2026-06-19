from __future__ import annotations

from tools._base import ToolException

def ner(text: str, model: str = "en_core_web_sm") -> str:
    """Named entity extraction via spaCy when available."""
    try:
        import spacy
        nlp = spacy.load(model)
        doc = nlp(text)
        return "\n".join(f"{ent.text} -> {ent.label_}" for ent in doc.ents)
    except Exception as e:
        raise ToolException(str(e)) from e
