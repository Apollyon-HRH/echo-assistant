from __future__ import annotations

from tools._shared import json_dump
from core.exceptions import ToolException

def vision(image_path: str, **kwargs) -> str:
    """Inspect an image with Pillow and optionally OCR it."""
    try:
        from PIL import Image, ExifTags
        img = Image.open(image_path)
        info = {
            "path": image_path,
            "format": img.format,
            "size": img.size,
            "mode": img.mode,
        }
        try:
            exif = img.getexif()
            info["exif_keys"] = [ExifTags.TAGS.get(k, k) for k in exif.keys()]
        except Exception:
            info["exif_keys"] = []
        return json_dump(info)
    except Exception as exc:
        raise ToolException(f"vision failed: {exc}")
