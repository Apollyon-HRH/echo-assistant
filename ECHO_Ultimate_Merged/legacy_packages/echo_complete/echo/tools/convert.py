import csv
import json
from pathlib import Path

from core.exceptions import ToolException
from tools._shared import json_read, json_write, yaml_read, yaml_write

def convert(input_path: str, output_path: str = "", target: str = "json") -> str:
    """Convert between CSV, JSON, YAML and XML formats."""
    try:
        src = Path(input_path)
        if not src.exists():
            raise ToolException(f"Arquivo não encontrado: {src}")
        out = Path(output_path) if output_path else src.with_suffix("." + target.lower())
        suffix = src.suffix.lower()
        if suffix == ".csv" and target.lower() == "json":
            with src.open("r", encoding="utf-8", newline="") as fh:
                rows = list(csv.DictReader(fh))
            json_write(out, rows)
        elif suffix == ".json" and target.lower() in {"yaml", "yml"}:
            yaml_write(out, json_read(src))
        elif suffix in {".yaml", ".yml"} and target.lower() == "json":
            json_write(out, yaml_read(src))
        elif suffix == ".json" and target.lower() == "xml":
            data = json_read(src)
            def to_xml(obj, tag="root"):
                from tools._shared import xml_escape
                if isinstance(obj, dict):
                    inner = "".join(to_xml(v, k) for k, v in obj.items())
                    return f"<{tag}>{inner}</{tag}>"
                if isinstance(obj, list):
                    return f"<{tag}>" + "".join(to_xml(i, "item") for i in obj) + f"</{tag}>"
                return f"<{tag}>{xml_escape(str(obj))}</{tag}>"
            out.write_text(to_xml(data), encoding="utf-8")
        else:
            raise ToolException(f"Conversão não suportada: {suffix} -> {target}")
        return f"Convertido para {out}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta convert: {e}") from e
