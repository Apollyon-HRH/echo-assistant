from __future__ import annotations

from tools._base import ToolException

def vision(image_path: str) -> str:
    """Basic image inspection using OpenCV."""
    try:
        import cv2
        img = cv2.imread(image_path)
        if img is None:
            raise ToolException("Unable to read image")
        h, w = img.shape[:2]
        mean = img.mean(axis=(0, 1))
        return f"size={w}x{h}; mean_bgr={mean.round(2).tolist()}"
    except Exception as e:
        raise ToolException(str(e)) from e
