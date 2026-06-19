"""Logging utilities for ECHO."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from colorama import Fore, Style, init as colorama_init

from core.config import CONFIG

colorama_init(autoreset=True)


class ColorFormatter(logging.Formatter):
    """Render log messages with colors for the console."""

    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        color = self.COLORS.get(record.levelno, "")
        return f"{color}{base}{Style.RESET_ALL}"


def setup_logger(name: str = "ECHO") -> logging.Logger:
    """Create and configure the main application logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level_name = CONFIG.get("logging", {}).get("level", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(level)

    log_path = Path(CONFIG.get("logging", {}).get("path", "./logs/echo.log"))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=int(CONFIG.get("logging", {}).get("max_size_mb", 5)) * 1024 * 1024,
        backupCount=int(CONFIG.get("logging", {}).get("max_files", 10)),
        encoding="utf-8",
    )
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger
