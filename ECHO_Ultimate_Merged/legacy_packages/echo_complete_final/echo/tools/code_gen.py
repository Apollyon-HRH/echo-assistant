from __future__ import annotations

from core.exceptions import ToolException

def code_gen(spec: str, language: str = "python") -> str:
    """Generate a starter template from a specification."""
    spec = spec.strip()
    if not spec:
        raise ToolException("spec cannot be empty")
    language = language.lower().strip()
    if language == "python":
        return f'''"""Generated code scaffold for: {spec}"""

from __future__ import annotations


def main() -> None:
    """Entry point."""
    print({spec!r})


if __name__ == "__main__":
    main()
'''
    if language in {"bash", "sh"}:
        return f"#!/usr/bin/env bash\necho {spec!r}\n"
    return f"// Generated scaffold for: {spec}"
