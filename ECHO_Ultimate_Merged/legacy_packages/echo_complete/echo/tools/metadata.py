from pathlib import Path

from core.exceptions import ToolException

def metadata(path: str) -> str:
    """Extract metadata from images and common media files."""
    try:
        p = Path(path)
        if not p.exists():
            raise ToolException(f"Arquivo não encontrado: {p}")
        info = {"name": p.name, "size_bytes": p.stat().st_size}
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            img = Image.open(p)
            info["image_size"] = img.size
            exif = img.getexif()
            if exif:
                info["exif"] = {TAGS.get(k, str(k)): v for k, v in exif.items()}
        except Exception:
            pass
        try:
            import subprocess, json
            result = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(p)], capture_output=True, text=True, timeout=20)
            if result.returncode == 0 and result.stdout:
                info["ffprobe"] = json.loads(result.stdout)
        except Exception:
            pass
        import json
        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta metadata: {e}") from e
