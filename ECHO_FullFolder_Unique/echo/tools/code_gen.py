from __future__ import annotations

from tools._shared import json_dump
from core.exceptions import ToolException

def code_gen(language: str, task: str, name: str = "generated_program", **kwargs) -> str:
    """Generate a scaffold with boilerplate and comments."""
    try:
        templates = {
            "python": f'"""Auto-generated: {task}"""\n\nfrom __future__ import annotations\n\n\ndef main() -> None:\n    print("Implementar: {task}")\n\n\nif __name__ == "__main__":\n    main()\n',
            "javascript": f'// Auto-generated: {task}\nfunction main() {{\n  console.log("Implementar: {task}");\n}}\nmain();\n',
            "xml": f'<!-- Auto-generated: {task} -->\n<root>Implementar: {task}</root>\n',
        }
        return json_dump({"name": name, "language": language, "code": templates.get(language.lower(), templates["python"])})
    except Exception as exc:
        raise ToolException(f"code_gen failed: {exc}")
