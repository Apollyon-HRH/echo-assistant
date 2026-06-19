from __future__ import annotations

from pathlib import Path
import importlib.util

class PluginManager:
    def __init__(self, config):
        self.config = config
        self.plugins_dir = Path(config.storage.plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded = {}

    def load_all(self):
        for file in self.plugins_dir.glob("*.py"):
            spec = importlib.util.spec_from_file_location(file.stem, file)
            if not spec or not spec.loader:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.loaded[file.stem] = mod

    def list(self):
        return list(self.loaded.keys())

    def call(self, name: str, *args, **kwargs):
        mod = self.loaded[name]
        if hasattr(mod, "run"):
            return mod.run(*args, **kwargs)
        raise AttributeError(f"plugin {name} has no run()")
