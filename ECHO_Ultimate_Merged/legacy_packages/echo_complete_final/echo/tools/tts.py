from __future__ import annotations

from pathlib import Path

from core.exceptions import ToolException
from ._shared import TEMP_DIR, ensure_parent

def tts(text: str, voice: str = "pt-BR-AntonioNeural", output_path: str | None = None) -> str:
    """Generate speech audio using edge-tts when available."""
    text = text.strip()
    if not text:
        raise ToolException("text cannot be empty")

    out = Path(output_path).expanduser() if output_path else TEMP_DIR / "tts.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import asyncio
        import edge_tts  # type: ignore

        async def _run():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(out))
        asyncio.run(_run())
        return str(out)
    except Exception as exc:
        raise ToolException(f"TTS failed: {exc}") from exc
