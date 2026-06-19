from pathlib import Path

from PIL import Image

from core.exceptions import ToolException

def image_convert(input_path: str, output_path: str = "", format: str = "png") -> str:
    """Convert image formats using Pillow."""
    try:
        src = Path(input_path)
        if not src.exists():
            raise ToolException(f"Arquivo não encontrado: {src}")
        out = Path(output_path) if output_path else src.with_suffix("." + format.lower())
        img = Image.open(src)
        img.save(out, format=format.upper())
        return f"Imagem convertida para {out}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta image_convert: {e}") from e
