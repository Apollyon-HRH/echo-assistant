"""Configuration loader for ECHO."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required to load config.yaml") from exc

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    def load_dotenv(*args, **kwargs):
        return False

from core.exceptions import ECHOError

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def _deep_get(data: Dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ECHOError(f"Missing configuration key: {path}")
        current = current[part]
    return current


def _expand_env(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        key = value[2:-1]
        return os.getenv(key, "")
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def _validate_types(config: Dict[str, Any]) -> None:
    web_search_enabled = _deep_get(config, "tools.web_search")
    if not isinstance(web_search_enabled, bool):
        raise TypeError("tools.web_search must be a boolean")

    max_tokens = _deep_get(config, "context.max_tokens")
    if not isinstance(max_tokens, int):
        raise TypeError("context.max_tokens must be an integer")

    level = _deep_get(config, "logging.level")
    if not isinstance(level, str):
        raise TypeError("logging.level must be a string")


def load_config() -> Dict[str, Any]:
    """Load YAML and environment variables into a single configuration mapping."""
    load_dotenv()
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing configuration file: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    config = _expand_env(data)
    _validate_types(config)
    return config


CONFIG = load_config()
