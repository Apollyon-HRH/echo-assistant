from __future__ import annotations

from pathlib import Path

from core.exceptions import ToolException
from ._shared import json_pretty

def vision(image_path: str, detect_faces: bool = True) -> str:
    """Basic computer vision analysis with OpenCV."""
    p = Path(image_path).expanduser()
    if not p.exists():
        raise ToolException(f"Image not found: {p}")

    try:
        import cv2
        img = cv2.imread(str(p))
        if img is None:
            raise ToolException("Could not decode image")
        h, w = img.shape[:2]
        result = {"width": w, "height": h, "channels": int(img.shape[2]) if len(img.shape) > 2 else 1}
        if detect_faces:
            try:
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                face_cascade = cv2.CascadeClassifier(cascade_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                result["faces"] = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for (x, y, w, h) in faces]
            except Exception:
                result["faces"] = []
        return json_pretty(result)
    except Exception as exc:
        raise ToolException(f"vision failed: {exc}") from exc
