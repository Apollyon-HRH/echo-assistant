from __future__ import annotations

from tools._base import ToolException

def ocr(image_path: str, lang: str = "eng") -> str:
    """Extract text from an image via Tesseract."""
    try:
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(image_path), lang=lang).strip()
    except Exception as e:
        raise ToolException(str(e)) from e
