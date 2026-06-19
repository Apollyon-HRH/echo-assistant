from core.exceptions import ToolException

def stt(audio_path: str, model: str = "base", language: str = "pt") -> str:
    """Transcribe audio locally using Whisper."""
    try:
        import whisper
        model_obj = whisper.load_model(model)
        result = model_obj.transcribe(audio_path, language=language)
        return result.get("text", "").strip()
    except Exception as e:
        raise ToolException(f"Erro na ferramenta stt: {e}") from e
