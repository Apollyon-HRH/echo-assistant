from __future__ import annotations
from jinja2 import Template

def report(title: str, body: str) -> str:
    tpl = Template("<html><head><title>{{ title }}</title></head><body><h1>{{ title }}</h1><pre>{{ body }}</pre></body></html>")
    return tpl.render(title=title, body=body)
