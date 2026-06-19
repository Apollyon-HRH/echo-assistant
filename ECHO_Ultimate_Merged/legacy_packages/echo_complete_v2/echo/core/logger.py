from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    LEVEL_COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }
except Exception:
    Fore = Style = None
    LEVEL_COLORS = {}

from core.config import CONFIG

class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        color = LEVEL_COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL if Style else ""
        return f"{color}{msg}{reset}"

def setup_logger(name: str = "ECHO") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, CONFIG["logging"]["level"].upper(), logging.INFO))
    log_path = Path(CONFIG["logging"]["path"])
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=int(CONFIG["logging"]["max_size_mb"]) * 1024 * 1024,
        backupCount=int(CONFIG["logging"]["max_files"]),
        encoding="utf-8",
    )
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_formatter = ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger
