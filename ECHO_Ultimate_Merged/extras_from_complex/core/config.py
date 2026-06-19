from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os

import yaml
from dotenv import load_dotenv

def _expand_env(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        return os.getenv(value[2:-1], "")
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value

@dataclass
class LoggingConfig:
    level: str
    path: str
    json: bool = False

@dataclass
class APIConfig:
    host: str
    port: int

@dataclass
class StorageConfig:
    session_dir: str
    kb_dir: str
    plugins_dir: str
    db_path: str

@dataclass
class AppConfig:
    raw: dict
    project: dict
    models: dict
    routing: dict
    tools: dict
    storage: StorageConfig
    logging: LoggingConfig
    permissions: dict
    api: APIConfig

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        load_dotenv(override=False)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data = _expand_env(data)

        api = data.get("api", {})
        storage = data.get("storage", {})
        logging = data.get("logging", {})

        api.setdefault("host", os.getenv("ECHO_API_HOST", "127.0.0.1"))
        api.setdefault("port", int(os.getenv("ECHO_API_PORT", "8080")))
        storage.setdefault("session_dir", "./data/sessions")
        storage.setdefault("kb_dir", "./data/kb")
        storage.setdefault("plugins_dir", "./plugins")
        storage.setdefault("db_path", os.getenv("ECHO_DB_PATH", "./data/echo.db"))
        logging.setdefault("level", "INFO")
        logging.setdefault("path", os.path.join(os.getenv("ECHO_LOG_DIR", "./logs"), "echo.log"))
        logging.setdefault("json", False)

        return cls(
            raw=data,
            project=data.get("project", {}),
            models=data.get("models", {}),
            routing=data.get("routing", {}),
            tools=data.get("tools", {}),
            storage=StorageConfig(**storage),
            logging=LoggingConfig(**logging),
            permissions=data.get("permissions", {}),
            api=APIConfig(**api),
        )
