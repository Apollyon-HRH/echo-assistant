"""Configuration loading and validation for ECHO."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import os

import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config.yaml"
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


def _expand_env(value: Any) -> Any:
    """Expand ${VAR} references in a YAML value."""
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_name = value[2:-1]
        return os.getenv(env_name, "")
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def _validate_config(cfg: dict[str, Any]) -> None:
    """Validate configuration types and required keys."""
    required_paths = ["project", "models", "context", "system_prompt", "logging", "telegram", "tools", "timeouts"]
    for key in required_paths:
        if key not in cfg:
            raise ValueError(f"Missing required config section: {key}")

    tools = cfg.get("tools", {})
    if not isinstance(tools.get("web_search"), bool):
        raise TypeError("tools.web_search must be boolean")
    if not isinstance(cfg["context"].get("max_tokens"), int):
        raise TypeError("context.max_tokens must be integer")
    if not isinstance(cfg["logging"].get("level"), str):
        raise TypeError("logging.level must be string")
    if not isinstance(cfg["telegram"].get("enabled"), bool):
        raise TypeError("telegram.enabled must be boolean")
    if not isinstance(cfg["timeouts"].get("ollama_request"), int):
        raise TypeError("timeouts.ollama_request must be integer")


def _load_yaml() -> dict[str, Any]:
    """Load YAML config from disk."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    return _expand_env(raw)


CONFIG = _load_yaml()
_validate_config(CONFIG)
