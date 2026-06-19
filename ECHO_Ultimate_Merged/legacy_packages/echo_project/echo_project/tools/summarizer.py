"""Text summarizer tool."""

from __future__ import annotations

import json
import re

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def summarizer(text: str, max_sentences: int = 5, **kwargs) -> str:
    """Summarize text using a heuristic excerpt."""
    try:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
        return " ".join(sentences[:max_sentences])
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
