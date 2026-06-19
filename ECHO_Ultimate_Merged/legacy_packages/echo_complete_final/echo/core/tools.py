from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .config import CONFIG
from .exceptions import ToolException
from .logger import setup_logger

logger = setup_logger("echo.tools")

class ToolRegistry:
    """Dynamic tool loader for the tools package."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or CONFIG
        self.tools: Dict[str, Callable[..., Any]] = {}
        self.descriptions: Dict[str, str] = {}
        self.load_tools()

    def load_tools(self) -> Dict[str, Callable[..., Any]]:
        package = importlib.import_module("tools")
        package_path = Path(package.__file__).resolve().parent

        for module_info in pkgutil.iter_modules([str(package_path)]):
            if module_info.name.startswith("_"):
                continue
            if module_info.name in {"__init__"}:
                continue
            enabled = self.config.get("tools", {}).get(module_info.name, True)
            if not enabled:
                continue

            module = importlib.import_module(f"tools.{module_info.name}")
            if hasattr(module, module_info.name):
                fn = getattr(module, module_info.name)
                if callable(fn):
                    self.tools[module_info.name] = fn
                    self.descriptions[module_info.name] = inspect.getdoc(fn) or inspect.getdoc(module) or ""
                    logger.debug("Loaded tool: %s", module_info.name)
        return self.tools

    def execute(self, tool_name: str, **kwargs):
        if tool_name not in self.tools:
            raise ToolException(f"Tool not available: {tool_name}")
        return self.tools[tool_name](**kwargs)

    def get_tool_list(self) -> List[dict]:
        return [
            {"name": name, "description": self.descriptions.get(name, "")}
            for name in sorted(self.tools.keys())
        ]
