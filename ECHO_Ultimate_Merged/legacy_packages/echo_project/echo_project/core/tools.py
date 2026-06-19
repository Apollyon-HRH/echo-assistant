"""Dynamic tool loader for ECHO."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import Any, Callable, Dict, List

from core.exceptions import ToolException


class ToolRegistry:
    """Load enabled tools dynamically from the tools package."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.enabled = config.get("tools", {})
        self.registry: Dict[str, Callable[..., str]] = {}
        self.load_tools()

    def load_tools(self) -> None:
        """Import tool modules whose config flag is enabled."""
        package = importlib.import_module("tools")
        package_path = package.__path__
        for module_info in pkgutil.iter_modules(package_path):
            name = module_info.name
            if name.startswith("_"):
                continue
            if not self.enabled.get(name, False):
                continue
            module = importlib.import_module(f"tools.{name}")
            func = getattr(module, name, None)
            if callable(func):
                self.registry[name] = func

    def execute(self, tool_name: str, **kwargs) -> str:
        """Execute a loaded tool."""
        if tool_name not in self.registry:
            raise ToolException(f"Tool not available: {tool_name}")
        func = self.registry[tool_name]
        return func(**kwargs)

    def get_tool_list(self) -> List[Dict[str, str]]:
        """Return the list of available tools with short descriptions."""
        items = []
        for name, func in sorted(self.registry.items()):
            doc = inspect.getdoc(func) or ""
            items.append({"name": name, "description": doc.splitlines()[0] if doc else ""})
        return items
