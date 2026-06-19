"""Code generation helper."""

from __future__ import annotations

from tools._common import ToolException


def code_gen(language: str, spec: str) -> str:
    """Generate a pragmatic starter template for common languages."""
    lang = language.lower().strip()
    if not spec.strip():
        raise ToolException("spec vazia.")

    if lang in {"python", "py"}:
        lines = [
            f'"""Generated starter: {spec}"""',
            "",
            "def main():",
            '    """Entry point."""',
            f"    print({spec!r})",
            "",
            'if __name__ == "__main__":',
            "    main()",
        ]
        return "\n".join(lines)

    if lang in {"javascript", "js"}:
        lines = [
            f"// Generated starter: {spec}",
            "function main() {",
            f"  console.log({spec!r});",
            "}",
            "main();",
        ]
        return "\n".join(lines)

    if lang == "html":
        lines = [
            "<!doctype html>",
            '<html lang="pt-BR">',
            '<head><meta charset="utf-8"><title>{}</title></head>'.format(spec),
            '<body><h1>{}</h1></body>'.format(spec),
            "</html>",
        ]
        return "\n".join(lines)

    return f"Sem template específico para {language}. Spec: {spec}"
