"""Dynamic tool registry for ECHO."""
from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List

from .exceptions import ToolException

TOOLS_PACKAGE = "tools"

class ToolRegistry:
    """Load and execute tools dynamically from the tools package."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Store configuration and load enabled tools."""
        self.config = config
        self.enabled = config.get("tools", {})
        self.tools: Dict[str, Callable[..., Any]] = {}
        self.descriptions: Dict[str, str] = {}
        self.load_tools()

    def _import_module(self, module_name: str) -> ModuleType:
        """Import a tool module."""
        return importlib.import_module(f"{TOOLS_PACKAGE}.{module_name}")

    def load_tools(self) -> None:
        """Import every enabled tool module and register its function."""
        package_dir = Path(__file__).resolve().parent.parent / TOOLS_PACKAGE
        for file in package_dir.glob("*.py"):
            if file.name.startswith("_") or file.name == "__init__.py":
                continue
            name = file.stem
            if not self.enabled.get(name, False):
                continue
            try:
                module = self._import_module(name)
                func = getattr(module, name, None)
                if callable(func):
                    self.tools[name] = func
                    self.descriptions[name] = inspect.getdoc(func) or f"{name} tool"
            except Exception as exc:
                self.descriptions[name] = f"Failed to load {name}: {exc}"

    def execute(self, tool_name: str, **kwargs: Any) -> Any:
        """Run a tool by name."""
        if tool_name not in self.tools:
            raise ToolException(f"Tool '{tool_name}' is not enabled or not available")
        try:
            return self.tools[tool_name](**kwargs)
        except ToolException:
            raise
        except Exception as exc:
            raise ToolException(f"Tool '{tool_name}' failed: {exc}") from exc

    def get_tool_list(self) -> List[Dict[str, str]]:
        """Return a user-friendly list of tools."""
        return [{"name": name, "description": desc} for name, desc in sorted(self.descriptions.items())]
