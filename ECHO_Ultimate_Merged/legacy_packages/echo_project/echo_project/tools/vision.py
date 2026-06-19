"""Basic vision inspection tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def vision(image_path: str, **kwargs) -> str:
    """Perform a lightweight vision summary using OpenCV."""
    try:
        import cv2
        img = cv2.imread(image_path)
        if img is None:
            raise ToolException("Could not open image")
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_brightness = float(gray.mean())
        return json_dump({"path": image_path, "width": w, "height": h, "mean_brightness": mean_brightness})
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
