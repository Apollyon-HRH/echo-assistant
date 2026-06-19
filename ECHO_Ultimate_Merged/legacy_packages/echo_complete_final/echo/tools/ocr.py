from __future__ import annotations

from pathlib import Path

from core.exceptions import ToolException

def ocr(image_path: str, lang: str = "eng") -> str:
    """Extract text from an image using Tesseract OCR."""
    p = Path(image_path).expanduser()
    if not p.exists():
        raise ToolException(f"Image not found: {p}")
    try:
        import pytesseract
        from PIL import Image
        text = pytesseract.image_to_string(Image.open(p), lang=lang)
        return text.strip()
    except Exception as exc:
        raise ToolException(f"OCR failed: {exc}") from exc
