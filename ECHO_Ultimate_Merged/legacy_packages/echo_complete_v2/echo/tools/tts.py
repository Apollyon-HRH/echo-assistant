from __future__ import annotations

from pathlib import Path

from tools._base import ToolException
from tools._utils import TEMP, now_stamp

def tts(text: str, voice: str = "pt-BR") -> str:
    """Text-to-speech using edge-tts when installed."""
    try:
        import asyncio
        import edge_tts

        async def _run():
            out = TEMP / f"tts_{now_stamp()}.mp3"
            communicate = edge_tts.Communicate(text=text, voice=f"{voice}-FranciscaNeural" if voice.startswith("pt") else "en-US-AriaNeural")
            await communicate.save(str(out))
            return str(out)

        return asyncio.run(_run())
    except Exception as e:
        raise ToolException(str(e)) from e
