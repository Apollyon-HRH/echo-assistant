from __future__ import annotations

from pathlib import Path
from tools._shared import json_dump
from core.exceptions import ToolException

def tts(text: str, output_path: str | None = None, **kwargs) -> str:
    """Text-to-speech with pyttsx3 or a simple placeholder file."""
    try:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            if output_path:
                engine.save_to_file(text, output_path)
                engine.runAndWait()
                return json_dump({"saved": output_path})
            engine.say(text)
            engine.runAndWait()
            return json_dump({"spoken": True})
        except Exception:
            if not output_path:
                raise
            Path(output_path).write_text(text, encoding="utf-8")
            return json_dump({"saved_text_fallback": output_path})
    except Exception as exc:
        raise ToolException(f"tts failed: {exc}")
