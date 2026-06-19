from pathlib import Path

from core.exceptions import ToolException

def report(title: str, content: str, output_path: str = "", format: str = "md") -> str:
    """Generate Markdown or HTML reports."""
    try:
        out = Path(output_path) if output_path else Path("temp") / f"{title.replace(' ', '_')}.{format.lower()}"
        out.parent.mkdir(parents=True, exist_ok=True)
        if format.lower() == "html":
            try:
                from jinja2 import Template
                tpl = Template("<html><head><meta charset='utf-8'><title>{{ title }}</title></head><body><h1>{{ title }}</h1><pre>{{ content }}</pre></body></html>")
                out.write_text(tpl.render(title=title, content=content), encoding="utf-8")
            except Exception:
                out.write_text(f"<html><body><h1>{title}</h1><pre>{content}</pre></body></html>", encoding="utf-8")
        else:
            out.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")
        return f"Relatório salvo em {out}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta report: {e}") from e
