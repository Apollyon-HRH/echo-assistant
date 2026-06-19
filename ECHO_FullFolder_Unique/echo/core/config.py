from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import os

import yaml
from dotenv import load_dotenv

from .exceptions import ConfigurationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

load_dotenv(PROJECT_ROOT / ".env", override=False)
load_dotenv(override=False)


def _expand_env(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        return os.getenv(value[2:-1], "")
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def _validate(config: Dict[str, Any]) -> None:
    if "tools" not in config or not isinstance(config["tools"], dict):
        raise ConfigurationError("config.yaml must contain a tools mapping")
    if not isinstance(config.get("context", {}).get("max_tokens", 0), int):
        raise ConfigurationError("context.max_tokens must be an integer")
    if not isinstance(config.get("system_prompt", ""), str):
        raise ConfigurationError("system_prompt must be a string")


def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    if not path.exists():
        raise ConfigurationError(f"Configuration file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data = _expand_env(data)
    data.setdefault("env", {})
    data["env"]["ollama_base_url"] = os.getenv("OLLAMA_BASE_URL", data["env"].get("ollama_base_url", "http://localhost:11434"))
    _validate(data)
    return data


CONFIG: Dict[str, Any] = load_config()


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
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        data = _expand_env(data)
        storage = data.get("storage", {})
        logging = data.get("logging", {})
        api = data.get("api", {})
        return cls(
            raw=data,
            project=data.get("project", {}),
            models=data.get("models", {}),
            routing=data.get("routing", {}),
            tools=data.get("tools", {}),
            storage=StorageConfig(
                session_dir=storage.get("session_dir", "./sessions/"),
                kb_dir=storage.get("kb_dir", "./memory/kb/"),
                plugins_dir=storage.get("plugins_dir", "./plugins/"),
                db_path=storage.get("db_path", "./data/echo.sqlite3"),
            ),
            logging=LoggingConfig(
                level=logging.get("level", "INFO"),
                path=logging.get("path", logging.get("file", "./logs/echo.log")),
                json=bool(logging.get("json", False)),
            ),
            permissions=data.get("permissions", {}),
            api=APIConfig(host=api.get("host", "127.0.0.1"), port=int(api.get("port", 8000))),
        )
