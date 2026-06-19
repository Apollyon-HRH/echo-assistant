from pathlib import Path

from core.exceptions import ToolException
from tools._shared import ensure_dir, safe_filename

def tts(text: str, voice: str = "pt-BR") -> str:
    """Generate speech audio using edge-tts."""
    try:
        import asyncio
        import edge_tts
        out = Path("temp") / f"{safe_filename(voice)}_{safe_filename(text[:24])}.mp3"
        ensure_dir(out.parent)

        async def _run() -> None:
            communicate = edge_tts.Communicate(text=text, voice=voice)
            await communicate.save(str(out))

        asyncio.run(_run())
        return f"Áudio salvo em {out}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta tts: {e}") from e
