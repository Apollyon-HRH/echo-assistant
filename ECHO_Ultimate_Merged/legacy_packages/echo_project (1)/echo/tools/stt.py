"""Speech-to-text transcription."""

from __future__ import annotations
from pathlib import Path

from tools._common import ToolException

def stt(audio_path: str, model: str = "base") -> str:
    """Transcribe audio using Whisper."""
    try:
        import whisper
        m = whisper.load_model(model)
        result = m.transcribe(audio_path)
        return result.get("text", "").strip()
    except Exception as e:
        raise ToolException(f"Falha no STT: {e}")
