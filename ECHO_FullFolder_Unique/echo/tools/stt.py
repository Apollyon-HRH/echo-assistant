from __future__ import annotations

from tools._shared import json_dump
from core.exceptions import ToolException

def stt(audio_path: str, **kwargs) -> str:
    """Speech-to-text using whisper/faster-whisper when installed."""
    try:
        try:
            import whisper
            model = whisper.load_model(kwargs.get("model", "base"))
            result = model.transcribe(audio_path)
            return json_dump(result)
        except Exception:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = r.record(source)
            return json_dump({"text": r.recognize_google(audio, language=kwargs.get("language", "pt-BR"))})
    except Exception as exc:
        raise ToolException(f"stt failed: {exc}")
