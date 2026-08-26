"""Structured logging utilities."""

import logging
import logging.config
from app.config import settings

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": settings.log_level,
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "detailed": {
            "level": settings.log_level,
            "class": "logging.StreamHandler",
            "formatter": "detailed",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": True,
        },
        "app": {
            "handlers": ["detailed"],
            "level": settings.log_level,
            "propagate": False,
        },
    },
}


def setup_logging():
    """Initialize logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
