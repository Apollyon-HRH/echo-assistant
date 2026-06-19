from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

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

def _load_env(config: Dict[str, Any]) -> Dict[str, Any]:
    env = config.setdefault("env", {})
    env["telegram_token"] = os.getenv("TELEGRAM_TOKEN", "")
    env["telegram_chat_id"] = os.getenv("TELEGRAM_CHAT_ID", "")
    env["google_api_key"] = os.getenv("GOOGLE_API_KEY", "")
    env["github_token"] = os.getenv("GITHUB_TOKEN", "")
    env["reddit_client_id"] = os.getenv("REDDIT_CLIENT_ID", "")
    env["reddit_client_secret"] = os.getenv("REDDIT_CLIENT_SECRET", "")
    env["twitter_bearer_token"] = os.getenv("TWITTER_BEARER_TOKEN", "")
    env["youtube_api_key"] = os.getenv("YOUTUBE_API_KEY", "")
    env["openweather_api_key"] = os.getenv("OPENWEATHER_API_KEY", "")
    env["smtp_server"] = os.getenv("SMTP_SERVER", "")
    env["smtp_port"] = int(os.getenv("SMTP_PORT", "587") or 587)
    env["smtp_user"] = os.getenv("SMTP_USER", "")
    env["smtp_password"] = os.getenv("SMTP_PASSWORD", "")
    env["home_assistant_url"] = os.getenv("HOME_ASSISTANT_URL", "")
    env["home_assistant_token"] = os.getenv("HOME_ASSISTANT_TOKEN", "")
    env["discord_webhook_url"] = os.getenv("DISCORD_WEBHOOK_URL", "")
    env["slack_webhook_url"] = os.getenv("SLACK_WEBHOOK_URL", "")
    env["translate_url"] = os.getenv("LIBRETRANSLATE_URL", "")
    env["image_gen_api_url"] = os.getenv("IMAGE_GEN_API_URL", "")
    env["image_gen_api_key"] = os.getenv("IMAGE_GEN_API_KEY", "")
    env["ollama_base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return config

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise ConfigurationError(f"Missing config file: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}
    config = _expand_env(config)
    _validate(config)
    return _load_env(config)

CONFIG = load_config()
