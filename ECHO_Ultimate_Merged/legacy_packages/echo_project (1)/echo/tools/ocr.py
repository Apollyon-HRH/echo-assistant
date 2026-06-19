"""OCR extraction from images."""

from __future__ import annotations
from pathlib import Path

from tools._common import ToolException

def ocr(image_path: str, lang: str = "por+eng") -> str:
    """Read text from an image using Tesseract."""
    try:
        from PIL import Image
        import pytesseract
        text = pytesseract.image_to_string(Image.open(image_path), lang=lang)
        return text.strip()
    except Exception as e:
        raise ToolException(f"Falha no OCR: {e}")
