"""Dynamic tool registry for ECHO."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any
import inspect

from tools._common import ToolException


class ToolRegistry:
    """Load and invoke enabled tools dynamically."""

    def __init__(self, config: dict[str, Any]):
        """Create a new registry."""
        self.config = config
        self.enabled = {name for name, on in (config.get("tools") or {}).items() if on}
        self.modules: dict[str, Any] = {}
        self.load_tools()

    def load_tools(self) -> None:
        """Import tool modules that are enabled in the configuration."""
        tools_dir = Path(__file__).resolve().parents[1] / "tools"
        for path in tools_dir.glob("*.py"):
            if path.name.startswith("_") or path.stem == "__init__":
                continue
            if path.stem not in self.enabled:
                continue
            try:
                self.modules[path.stem] = import_module(f"tools.{path.stem}")
            except Exception as e:
                self.modules[path.stem] = e

    def get_tool_list(self) -> list[dict[str, str]]:
        """Return a list describing loaded tools."""
        out = []
        for name, mod in sorted(self.modules.items()):
            if isinstance(mod, Exception):
                continue
            fn = getattr(mod, name, None)
            desc = inspect.getdoc(fn) or "Sem descrição."
            out.append({"name": name, "description": desc.splitlines()[0] if desc else ""})
        return out

    def execute(self, tool_name: str, **kwargs) -> str:
        """Execute a named tool with keyword arguments."""
        if tool_name not in self.modules:
            raise ToolException(f"Ferramenta indisponível: {tool_name}")
        mod = self.modules[tool_name]
        if isinstance(mod, Exception):
            raise ToolException(f"Falha ao carregar ferramenta {tool_name}: {mod}")
        fn = getattr(mod, tool_name, None)
        if not callable(fn):
            raise ToolException(f"Ferramenta inválida: {tool_name}")
        return fn(**kwargs)
