"""Structured application logger for performance, RAG metrics, and error tracking.

Configures console and file log handlers targeting `logs/app.log`.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from backend.config.settings import get_settings


class JSONLogFormatter(logging.Formatter):
    """Custom log formatter rendering log records as structured JSON strings."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record into a structured JSON string.

        Args:
            record: Python logging LogRecord instance.

        Returns:
            str: Standardized JSON log representation.
        """
        log_object: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Standard built-in LogRecord attribute names to ignore when capturing custom extra attributes
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message"
        }

        # Dynamically include any custom extra attributes passed to logger calls
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                try:
                    # Test JSON serializability
                    json.dumps({key: value})
                    log_object[key] = value
                except (TypeError, OverflowError):
                    log_object[key] = str(value)

        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_object)


def setup_logging(log_level: Optional[str] = None) -> None:
    """Configure global Python logging handlers (Console & File).

    Args:
        log_level: Optional log level string override (DEBUG, INFO, WARNING, ERROR).
    """
    settings = get_settings()
    level_str = log_level or settings.log_level
    numeric_level = getattr(logging, level_str.upper(), logging.INFO)

    log_dir = settings.get_absolute_log_dir()
    log_file_path = log_dir / "app.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Avoid duplicate handlers on re-initialization
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # JSON File Handler
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(JSONLogFormatter())

    # Console Standard Stream Handler (Clean human-readable format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Suppress verbose third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retrieve named logger instance configured with application standards.

    Args:
        name: Logger name identifier (typically __name__).

    Returns:
        logging.Logger: Named logger instance.
    """
    return logging.getLogger(name)
