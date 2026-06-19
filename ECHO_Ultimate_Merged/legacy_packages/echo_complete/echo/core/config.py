"""Configuration loading and validation for ECHO."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from .exceptions import ConfigError

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"

def _expand_env_vars(value: Any) -> Any:
    """Recursively expand ${VAR} expressions in configuration values."""
    if isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env_vars(v) for v in value]
    if isinstance(value, str):
        def repl(match: re.Match[str]) -> str:
            return os.getenv(match.group(1), "")
        return re.sub(r"\$\{([A-Z0-9_]+)\}", repl, value)
    return value

def _validate_config(cfg: Dict[str, Any]) -> None:
    """Validate the minimum configuration types required by the project."""
    try:
        if not isinstance(cfg["tools"]["web_search"], bool):
            raise ConfigError("tools.web_search must be boolean")
        if not isinstance(cfg["context"]["max_tokens"], int):
            raise ConfigError("context.max_tokens must be integer")
        if not isinstance(cfg["logging"]["level"], str):
            raise ConfigError("logging.level must be string")
    except KeyError as exc:
        raise ConfigError(f"Missing required configuration key: {exc}") from exc

def load_config() -> Dict[str, Any]:
    """Load config.yaml and .env, then return a validated dictionary."""
    load_dotenv(ENV_PATH, override=False)
    config_path = ROOT / "config.yaml"
    if not config_path.exists():
        raise ConfigError("config.yaml not found")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError("config.yaml must contain a mapping at the top level")

    cfg = _expand_env_vars(raw)
    _validate_config(cfg)
    return cfg

CONFIG = load_config()
