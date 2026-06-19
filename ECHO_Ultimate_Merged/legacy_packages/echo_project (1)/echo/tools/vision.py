"""Basic image inspection tool."""

from __future__ import annotations

from tools._common import ToolException


def vision(image_path: str, with_ocr: bool = False) -> str:
    """Inspect image size, format, and optional OCR."""
    try:
        from PIL import Image
        img = Image.open(image_path)
        info = [f"format={img.format}", f"size={img.size}", f"mode={img.mode}"]
        if with_ocr:
            try:
                import pytesseract
                info.append("ocr=" + pytesseract.image_to_string(img)[:2000].strip())
            except Exception as e:
                info.append(f"ocr_error={e}")
        return "\n".join(info)
    except Exception as e:
        raise ToolException(f"Falha na visão: {e}")
