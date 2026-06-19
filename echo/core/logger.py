"""
core/logger.py - Configuração de logging com rotação e cores.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init

init(autoreset=True)

LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

class ColoredFormatter(logging.Formatter):
    """Formatter que adiciona cores aos níveis de log."""
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(level=logging.INFO, name="echo"):
    """Configura e retorna um logger com handlers de console e arquivo."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evita duplicação de handlers
    if logger.handlers:
        return logger

    # Handler de arquivo com rotação
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "echo.log"),
        maxBytes=5*1024*1024,
        backupCount=10,
        encoding="utf-8"
    )
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Handler de console com cores
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

def get_logger(name="echo"):
    """Retorna o logger configurado."""
    return logging.getLogger(name)