"""Generate reports in Markdown or HTML."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from jinja2 import Template

from tools._common import ensure_parent, safe_json_dump, safe_json_load


REPORT_TEMPLATE = Template("""
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 960px; margin: 40px auto; line-height: 1.6; }
    h1, h2, h3 { color: #222; }
    pre { background: #f6f8fa; padding: 12px; overflow-x: auto; }
    code { background: #f6f8fa; padding: 2px 4px; }
    .meta { color: #666; font-size: 0.9em; }
  </style>
</head>
<body>
  <h1>{{ title }}</h1>
  <div class="meta">{{ subtitle }}</div>
  {% for section in sections %}
    <h2>{{ section.title }}</h2>
    {% if section.body %}<p>{{ section.body }}</p>{% endif %}
    {% if section.items %}
      <ul>{% for item in section.items %}<li>{{ item }}</li>{% endfor %}</ul>
    {% endif %}
    {% if section.table %}
      <table border="1" cellpadding="6" cellspacing="0">
        <thead><tr>{% for head in section.table.headers %}<th>{{ head }}</th>{% endfor %}</tr></thead>
        <tbody>
        {% for row in section.table.rows %}
          <tr>{% for cell in row %}<td>{{ cell }}</td>{% endfor %}</tr>
        {% endfor %}
        </tbody>
      </table>
    {% endif %}
  {% endfor %}
</body>
</html>
""")


def generate_report(data: dict[str, Any], output_path: str, format: str = "md") -> str:
    """Generate a report from structured data."""
    path = Path(output_path)
    ensure_parent(path)
    if format.lower() == "html":
        html = REPORT_TEMPLATE.render(
            title=data.get("title", "Report"),
            subtitle=data.get("subtitle", ""),
            sections=data.get("sections", []),
        )
        path.write_text(html, encoding="utf-8")
    else:
        lines = [f"# {data.get('title', 'Report')}"]
        if data.get("subtitle"):
            lines.append(f"_{data['subtitle']}_")
        for section in data.get("sections", []):
            lines.append(f"## {section.get('title', '')}")
            if section.get("body"):
                lines.append(section["body"])
            if section.get("items"):
                lines.extend([f"- {item}" for item in section["items"]])
        path.write_text("\n\n".join(lines), encoding="utf-8")
    return str(path)
