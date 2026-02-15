"""Logging configuration."""
import logging
import sys
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def add_fields(
        self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["timestamp"] = self.formatTime(record, self.datefmt)


def setup_logging() -> logging.Logger:
    """Configure application logging."""
    logger = logging.getLogger("loyalty_api")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    if settings.log_format == "json":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()
