from __future__ import annotations

from tools._base import ToolException

def stt(audio_path: str, model: str = "base") -> str:
    """Speech-to-text via Whisper."""
    try:
        import whisper
        m = whisper.load_model(model)
        result = m.transcribe(audio_path)
        return result.get("text", "").strip()
    except Exception as e:
        raise ToolException(str(e)) from e
