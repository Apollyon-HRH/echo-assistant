from __future__ import annotations

from tools._shared import json_dump
from core.exceptions import ToolException

def ocr(image_path: str, lang: str = "por", **kwargs) -> str:
    """Run OCR on an image when pytesseract is available."""
    try:
        from PIL import Image
        import pytesseract
        text = pytesseract.image_to_string(Image.open(image_path), lang=lang)
        return json_dump({"image": image_path, "text": text})
    except Exception as exc:
        raise ToolException(f"ocr failed: {exc}")
