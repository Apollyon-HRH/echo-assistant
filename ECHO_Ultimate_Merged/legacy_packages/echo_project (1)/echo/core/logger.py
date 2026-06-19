"""Logging setup for ECHO."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from colorama import Fore, Style, init as colorama_init

from core.config import CONFIG, BASE_DIR

colorama_init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Colorized console formatter."""

    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format a record with a level color."""
        msg = super().format(record)
        return f"{self.LEVEL_COLORS.get(record.levelno, '')}{msg}{Style.RESET_ALL}"


def setup_logger(name: str = "echo", level: Optional[str] = None) -> logging.Logger:
    """Create and configure the application logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_level = getattr(logging, (level or CONFIG["logging"]["level"]).upper(), logging.INFO)
    logger.setLevel(log_level)

    log_path = Path(CONFIG["logging"]["path"])
    if not log_path.is_absolute():
        log_path = (BASE_DIR / log_path).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=int(CONFIG["logging"]["max_size_mb"]) * 1024 * 1024,
        backupCount=int(CONFIG["logging"]["max_files"]),
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(fmt._fmt))
    console_handler.setLevel(log_level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger
