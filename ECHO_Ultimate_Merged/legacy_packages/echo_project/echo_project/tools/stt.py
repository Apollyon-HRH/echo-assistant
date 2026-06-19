"""Speech-to-text tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def stt(audio_path: str, language: str = "pt", **kwargs) -> str:
    """Transcribe audio using Whisper."""
    try:
        import whisper
        model_name = kwargs.get("model", "base")
        model = whisper.load_model(model_name)
        result = model.transcribe(audio_path, language=None if language == "auto" else language)
        return result.get("text", "").strip()
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
