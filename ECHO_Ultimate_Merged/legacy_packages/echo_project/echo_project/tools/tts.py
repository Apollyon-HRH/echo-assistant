"""Text-to-speech tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def tts(text: str, voice: str = "pt-BR", output_path: str | None = None, **kwargs) -> str:
    """Generate speech using Edge TTS."""
    try:
        import asyncio
        import tempfile
        import edge_tts
        from pathlib import Path
        out = Path(output_path or (Path(tempfile.gettempdir()) / "echo_tts.mp3"))
        async def _run():
            communicate = edge_tts.Communicate(text=text, voice=voice)
            await communicate.save(str(out))
        asyncio.run(_run())
        return str(out)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
