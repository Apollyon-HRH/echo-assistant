from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(level: str, log_path: str, json_logs: bool = False) -> logging.Logger:
    logger = logging.getLogger("echo")
    logger.setLevel(level.upper())
    logger.handlers.clear()

    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    console_handler = logging.StreamHandler()

    if json_logs:
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                payload = {
                    "time": self.formatTime(record),
                    "level": record.levelname,
                    "name": record.name,
                    "message": record.getMessage(),
                }
                return json.dumps(payload, ensure_ascii=False)
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
