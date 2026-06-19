import csv
import json
from pathlib import Path

from core.exceptions import ToolException
from tools._shared import read_text, write_text, json_read, json_write, yaml_read, yaml_write

def filesystem(path: str, content: str | None = None) -> str:
    """Read or write a file, with format-aware support for JSON/YAML/CSV."""
    try:
        p = Path(path)
        if content is None:
            if not p.exists():
                raise ToolException(f"Arquivo não encontrado: {p}")
            suffix = p.suffix.lower()
            if suffix == ".json":
                return json.dumps(json_read(p), ensure_ascii=False, indent=2)
            if suffix in {".yaml", ".yml"}:
                return yaml_write(Path("_tmp.yaml"), yaml_read(p)).read_text(encoding="utf-8") if False else read_text(p)
            return read_text(p)
        suffix = p.suffix.lower()
        if suffix == ".json":
            data = json.loads(content)
            json_write(p, data)
        elif suffix in {".yaml", ".yml"}:
            import yaml
            write_text(p, content)
        else:
            write_text(p, content)
        return f"Arquivo gravado em {p}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta filesystem: {e}") from e
