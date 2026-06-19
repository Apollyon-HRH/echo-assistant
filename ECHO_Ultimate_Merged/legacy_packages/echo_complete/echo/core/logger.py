"""Logging setup with rotating files and colored console output."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from colorama import Fore, Style, init as colorama_init

from .config import CONFIG

colorama_init(autoreset=True)

class ColorFormatter(logging.Formatter):
    """Colorize log records for console output."""

    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with ANSI colors."""
        base = super().format(record)
        color = self.LEVEL_COLORS.get(record.levelno, "")
        return f"{color}{base}{Style.RESET_ALL}"

def setup_logger(name: str = "echo", level: Optional[str] = None) -> logging.Logger:
    """Create and return the configured project logger."""
    cfg = CONFIG["logging"]
    log_level = getattr(logging, (level or cfg.get("level", "INFO")).upper(), logging.INFO)
    logger = logging.getLogger(name)
    if logger.handlers:
        logger.setLevel(log_level)
        return logger

    logger.setLevel(log_level)
    log_path = Path(cfg.get("path", "./logs/echo.log"))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=int(cfg.get("max_size_mb", 5)) * 1024 * 1024,
        backupCount=int(cfg.get("max_files", 10)),
        encoding="utf-8",
    )
    file_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_fmt)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    console_handler.setLevel(log_level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    logger.debug("Logger initialised")
    return logger
