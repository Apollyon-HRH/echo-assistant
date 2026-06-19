from __future__ import annotations
from pathlib import Path
import zipfile

def archive(source: str, dest_zip: str) -> str:
    src = Path(source)
    dst = Path(dest_zip)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        if src.is_dir():
            for p in src.rglob("*"):
                if p.is_file():
                    z.write(p, arcname=p.relative_to(src.parent))
        else:
            z.write(src, arcname=src.name)
    return str(dst)
