"""Structured logging setup for the Sage — Employee AI Assistant backend."""

import logging
import os

_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=_LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(_LOG_LEVEL)
    return logger
