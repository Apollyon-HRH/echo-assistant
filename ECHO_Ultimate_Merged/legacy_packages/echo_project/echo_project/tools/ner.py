"""Named entity recognition tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def ner(text: str, **kwargs) -> str:
    """Extract named entities using spaCy if available."""
    try:
        try:
            import spacy
            try:
                nlp = spacy.load("pt_core_news_sm")
            except Exception:
                nlp = spacy.blank("pt")
            doc = nlp(text)
            ents = [{"text": ent.text, "label": ent.label_} for ent in getattr(doc, "ents", [])]
            return json_dump(ents)
        except Exception as exc:
            raise ToolException(f"NER backend unavailable: {exc}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
