"""Text-to-speech using edge-tts."""

from __future__ import annotations
from pathlib import Path
import asyncio

from tools._common import ToolException, TEMP_DIR, ensure_parent

async def _tts_async(text: str, voice: str, output_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(output_path)

def tts(text: str, voice: str = "pt-BR-FranciscaNeural", output_path: str | None = None) -> str:
    """Render speech audio to a file."""
    out = Path(output_path) if output_path else TEMP_DIR / "tts_output.mp3"
    ensure_parent(out)
    try:
        asyncio.run(_tts_async(text, voice, str(out)))
        return str(out)
    except Exception as e:
        raise ToolException(f"Falha no TTS: {e}")
