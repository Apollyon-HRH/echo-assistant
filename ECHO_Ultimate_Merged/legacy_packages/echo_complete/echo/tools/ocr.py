from core.exceptions import ToolException

def ocr(image_path: str, lang: str = "eng") -> str:
    """Extract text from an image using Tesseract."""
    try:
        from PIL import Image
        import pytesseract
        text = pytesseract.image_to_string(Image.open(image_path), lang=lang)
        return text.strip()
    except Exception as e:
        raise ToolException(f"Erro na ferramenta ocr: {e}") from e
