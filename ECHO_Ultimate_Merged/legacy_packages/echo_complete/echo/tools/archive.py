import gzip
import tarfile
import zipfile
from pathlib import Path

from core.exceptions import ToolException

def archive(path: str, action: str = "zip", output: str = "") -> str:
    """Compress or extract ZIP/TAR/GZ archives."""
    try:
        p = Path(path)
        if action == "zip":
            out = Path(output) if output else p.with_suffix(".zip")
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
                if p.is_dir():
                    for file in p.rglob("*"):
                        if file.is_file():
                            zf.write(file, file.relative_to(p))
                else:
                    zf.write(p, p.name)
            return f"ZIP criado em {out}"
        if action == "unzip":
            out_dir = Path(output) if output else p.with_suffix("")
            out_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(p, "r") as zf:
                zf.extractall(out_dir)
            return f"ZIP extraído em {out_dir}"
        if action == "untar":
            out_dir = Path(output) if output else p.with_suffix("")
            out_dir.mkdir(parents=True, exist_ok=True)
            with tarfile.open(p, "r:*") as tf:
                tf.extractall(out_dir)
            return f"Arquivo extraído em {out_dir}"
        if action == "gunzip":
            out = Path(output) if output else p.with_suffix("")
            with gzip.open(p, "rb") as src, out.open("wb") as dst:
                dst.write(src.read())
            return f"GZ descompactado em {out}"
        raise ToolException(f"Ação inválida: {action}")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta archive: {e}") from e
