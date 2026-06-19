"""Named entity recognition."""

from __future__ import annotations
import json
import re

from tools._common import ToolException

def ner(text: str) -> str:
    """Extract named entities using spaCy if available, else regex heuristics."""
    try:
        try:
            import spacy
            try:
                nlp = spacy.load("pt_core_news_sm")
            except Exception:
                nlp = spacy.blank("pt")
            doc = nlp(text)
            ents = [{"text": e.text, "label": e.label_} for e in doc.ents]
            if ents:
                return json.dumps(ents, ensure_ascii=False, indent=2)
        except Exception:
            pass
        ents = re.findall(r"\b[A-ZÀ-Ý][\wÀ-ÿ]+(?:\s+[A-ZÀ-Ý][\wÀ-ÿ]+)*\b", text)
        return json.dumps([{"text": e, "label": "PROPN"} for e in ents], ensure_ascii=False, indent=2)
    except Exception as e:
        raise ToolException(f"Falha no NER: {e}")
