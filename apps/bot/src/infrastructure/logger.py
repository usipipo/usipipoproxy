"""
Sistema de logging para el bot uSipipo Telegram.

Author: uSipipo Team
Version: 1.0.0
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "usipipo-bot", level: str = "INFO") -> logging.Logger:
    """Configura y retorna un logger con formato consistente."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

    return logger


logger = setup_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Retorna un logger con el nombre especificado o el logger por defecto."""
    if name:
        return logging.getLogger(f"usipipo-bot.{name}")
    return logger
