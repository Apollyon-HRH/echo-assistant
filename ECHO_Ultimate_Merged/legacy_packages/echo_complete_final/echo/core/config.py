from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from .exceptions import ConfigurationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)
load_dotenv(override=False)

def _as_bool(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ConfigurationError(f"Config '{name}' must be boolean, got {type(value).__name__}")

def _merge_env(config: Dict[str, Any]) -> Dict[str, Any]:
    config.setdefault("env", {})
    config["env"]["telegram_token"] = os.getenv("TELEGRAM_TOKEN", "")
    config["env"]["google_api_key"] = os.getenv("GOOGLE_API_KEY", "")
    config["env"]["github_token"] = os.getenv("GITHUB_TOKEN", "")
    config["env"]["reddit_client_id"] = os.getenv("REDDIT_CLIENT_ID", "")
    config["env"]["reddit_client_secret"] = os.getenv("REDDIT_CLIENT_SECRET", "")
    config["env"]["twitter_bearer_token"] = os.getenv("TWITTER_BEARER_TOKEN", "")
    config["env"]["youtube_api_key"] = os.getenv("YOUTUBE_API_KEY", "")
    config["env"]["openweather_api_key"] = os.getenv("OPENWEATHER_API_KEY", "")
    config["env"]["smtp_server"] = os.getenv("SMTP_SERVER", "")
    config["env"]["smtp_port"] = int(os.getenv("SMTP_PORT", "587") or 587)
    config["env"]["smtp_user"] = os.getenv("SMTP_USER", "")
    config["env"]["smtp_password"] = os.getenv("SMTP_PASSWORD", "")
    config["env"]["home_assistant_url"] = os.getenv("HOME_ASSISTANT_URL", "")
    config["env"]["home_assistant_token"] = os.getenv("HOME_ASSISTANT_TOKEN", "")
    config["env"]["discord_webhook_url"] = os.getenv("DISCORD_WEBHOOK_URL", "")
    config["env"]["slack_webhook_url"] = os.getenv("SLACK_WEBHOOK_URL", "")
    config["env"]["translate_url"] = os.getenv("LIBRETRANSLATE_URL", "")
    config["env"]["a1111_url"] = os.getenv("IMAGE_GEN_API_URL", "")
    config["env"]["a1111_api_key"] = os.getenv("IMAGE_GEN_API_KEY", "")
    return config

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise ConfigurationError(f"Missing config file: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}
    if "tools" not in config:
        raise ConfigurationError("Missing 'tools' section in config.yaml")
    for tool_name, enabled in config["tools"].items():
        _as_bool(enabled, f"tools.{tool_name}")
    config = _merge_env(config)

    project_name = config.get("project", {}).get("name", "ECHO")
    if not isinstance(project_name, str):
        raise ConfigurationError("project.name must be a string")

    context = config.setdefault("context", {})
    context["max_tokens"] = int(context.get("max_tokens", 8192))
    context["save_history"] = bool(context.get("save_history", True))
    context["history_path"] = str(context.get("history_path", "./sessions/"))
    context["auto_summarize"] = bool(context.get("auto_summarize", True))

    logging_cfg = config.setdefault("logging", {})
    logging_cfg["level"] = str(logging_cfg.get("level", "INFO")).upper()
    logging_cfg["path"] = str(logging_cfg.get("path", "./logs/echo.log"))
    logging_cfg["max_files"] = int(logging_cfg.get("max_files", 10))
    logging_cfg["max_size_mb"] = int(logging_cfg.get("max_size_mb", 5))

    telegram = config.setdefault("telegram", {})
    telegram["enabled"] = bool(telegram.get("enabled", True))
    telegram["allowed_updates"] = telegram.get("allowed_updates", ["message", "edited_message", "callback_query"])

    config.setdefault("runtime", {})
    config["runtime"]["root"] = str(PROJECT_ROOT)
    config["runtime"]["temp_path"] = str(Path(config.get("temp_path", "./temp")))
    return config

CONFIG = load_config()
