from pathlib import Path

from core.exceptions import ToolException

def vision(image_path: str, action: str = "describe") -> str:
    """Perform simple computer vision tasks such as face detection or description."""
    try:
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is None:
                raise ToolException("Imagem inválida")
            if action == "faces":
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                faces = cv2.CascadeClassifier(cascade_path).detectMultiScale(gray, 1.1, 4)
                return f"{len(faces)} face(s) detectada(s)"
            h, w = img.shape[:2]
            return f"Imagem carregada: {w}x{h} pixels"
        except Exception:
            from PIL import Image
            img = Image.open(image_path)
            return f"Imagem carregada: {img.size[0]}x{img.size[1]} pixels, modo {img.mode}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta vision: {e}") from e
