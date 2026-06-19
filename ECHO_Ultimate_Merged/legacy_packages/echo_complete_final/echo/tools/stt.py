from __future__ import annotations

from pathlib import Path

from core.exceptions import ToolException

def stt(audio_path: str, model_size: str = "base", language: str | None = None) -> str:
    """Transcribe audio with Whisper when available."""
    p = Path(audio_path).expanduser()
    if not p.exists():
        raise ToolException(f"Audio not found: {p}")
    try:
        import whisper  # type: ignore
        model = whisper.load_model(model_size)
        result = model.transcribe(str(p), language=language)
        return result.get("text", "").strip()
    except Exception as exc:
        raise ToolException(f"STT failed: {exc}") from exc
