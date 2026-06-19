from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any, Callable, Dict, List

from tools._base import ToolException

class ToolRegistry:
    """Dynamic loader for tools package."""

    def __init__(self, config: dict):
        self.config = config
        self.tools: Dict[str, Callable[..., Any]] = {}
        self.load_tools()

    def load_tools(self) -> None:
        tools_dir = Path(__file__).resolve().parents[1] / "tools"
        for path in tools_dir.glob("*.py"):
            if path.name.startswith("_") or path.name == "__init__.py":
                continue
            module_name = f"tools.{path.stem}"
            module = importlib.import_module(module_name)
            func = getattr(module, path.stem, None)
            if callable(func) and self.config.get("tools", {}).get(path.stem, False):
                self.tools[path.stem] = func

    def execute(self, tool_name: str, **kwargs) -> str:
        if tool_name not in self.tools:
            raise ToolException(f"Tool not available: {tool_name}")
        result = self.tools[tool_name](**kwargs)
        return result if isinstance(result, str) else str(result)

    def get_tool_list(self) -> List[dict]:
        out = []
        for name, fn in sorted(self.tools.items()):
            doc = inspect.getdoc(fn) or ""
            out.append({"name": name, "description": doc.splitlines()[0] if doc else ""})
        return out
