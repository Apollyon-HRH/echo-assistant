from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Any, Callable, Dict, List

from .config import CONFIG
from .exceptions import ToolException
from .logger import setup_logger

logger = setup_logger("echo.tools")

class ToolRegistry:
    """Load enabled tools dynamically from the tools package."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or CONFIG
        self.tools: Dict[str, Callable[..., Any]] = {}
        self.descriptions: Dict[str, str] = {}
        self.load_tools()

    def load_tools(self) -> Dict[str, Callable[..., Any]]:
        package = importlib.import_module("tools")
        package_path = Path(package.__file__).resolve().parent
        for module_info in pkgutil.iter_modules([str(package_path)]):
            name = module_info.name
            if name.startswith("_") or name == "__init__":
                continue
            enabled = self.config.get("tools", {}).get(name, True)
            if not enabled:
                continue
            try:
                module = importlib.import_module(f"tools.{name}")
            except Exception as exc:
                logger.warning("Skipping tool %s: %s", name, exc)
                continue
            func = getattr(module, name, None)
            if callable(func):
                self.tools[name] = func
                doc = inspect.getdoc(func) or inspect.getdoc(module) or ""
                self.descriptions[name] = doc.splitlines()[0] if doc else ""
                logger.info("Loaded tool: %s", name)
        return self.tools

    def execute(self, tool_name: str, **kwargs):
        if tool_name not in self.tools:
            raise ToolException(f"Tool not available: {tool_name}")
        return self.tools[tool_name](**kwargs)

    def get_tool_list(self) -> List[dict]:
        return [{"name": k, "description": self.descriptions.get(k, "")} for k in sorted(self.tools)]
