"""
Logging module for slap-trigger.
Provides file logging with rotation support.
"""

import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


# Default log settings
DEFAULT_LOG_DIR = Path.home() / ".local" / "share" / "slap-trigger" / "logs"
DEFAULT_LOG_FILE = "slap-trigger.log"
DEFAULT_MAX_BYTES = 1024 * 1024  # 1MB
DEFAULT_BACKUP_COUNT = 1
DEFAULT_LEVEL = logging.INFO


def get_log_level(level_str: str) -> int:
    """Convert string log level to logging constant."""
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    return level_map.get(level_str.lower(), logging.INFO)


def setup_logger(
    log_dir: Path | str | None = None,
    log_file: str = DEFAULT_LOG_FILE,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
    level: int = DEFAULT_LEVEL,
    console: bool = False,
) -> logging.Logger:
    """Setup and return the application logger.

    Args:
        log_dir: Directory for log files (default: ~/.local/share/slap-trigger/logs/)
        log_file: Name of the log file
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        level: Logging level
        console: Also print logs to console (for debugging)

    Returns:
        Configured logger instance
    """
    # Use default log directory if not specified
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR
    else:
        log_dir = Path(log_dir)

    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / log_file

    # Create logger
    logger = logging.getLogger("slap_trigger")
    logger.setLevel(level)
    logger.handlers.clear()  # Remove any existing handlers

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = logging.Formatter(
        "[%(levelname)s] %(message)s",
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Optional console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


# Convenience functions
def log_debug(msg: str) -> None:
    """Log debug message."""
    logging.getLogger("slap_trigger").debug(msg)


def log_info(msg: str) -> None:
    """Log info message."""
    logging.getLogger("slap_trigger").info(msg)


def log_warning(msg: str) -> None:
    """Log warning message."""
    logging.getLogger("slap_trigger").warning(msg)


def log_error(msg: str) -> None:
    """Log error message."""
    logging.getLogger("slap_trigger").error(msg)


def log_exception(msg: str) -> None:
    """Log exception with traceback."""
    logging.getLogger("slap_trigger").exception(msg)
