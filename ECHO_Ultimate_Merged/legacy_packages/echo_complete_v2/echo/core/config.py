from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.yaml"
ENV_PATH = ROOT / ".env"

load_dotenv(ENV_PATH)

def _substitute_env(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        key = value[2:-1]
        return os.getenv(key, "")
    if isinstance(value, dict):
        return {k: _substitute_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_substitute_env(v) for v in value]
    return value

def _validate_config(cfg: Dict[str, Any]) -> None:
    if not isinstance(cfg.get("tools", {}).get("web_search"), bool):
        raise TypeError("tools.web_search must be boolean")
    if not isinstance(cfg.get("context", {}).get("max_tokens"), int):
        raise TypeError("context.max_tokens must be integer")
    if not isinstance(cfg.get("logging", {}).get("level"), str):
        raise TypeError("logging.level must be string")

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg = _substitute_env(cfg)
    _validate_config(cfg)
    return cfg

CONFIG = load_config()
