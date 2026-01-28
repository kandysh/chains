"""
Logging Configuration - COMPLETE IMPLEMENTATION
Structured logging setup for the entire application.
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = "app.log") -> None:
    """
    Configure application-wide logging.

    Sets up both file and console handlers with appropriate formatters.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file

    Example:
        >>> setup_logging("DEBUG", "trade_system.log")
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / log_file

    # Define log format
    log_format = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler - INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler - DEBUG and above
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Set specific log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Log startup message
    root_logger.info(f"Logging initialized - Level: {log_level}, File: {log_path}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the logger (typically __name__ of the module)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    return logging.getLogger(name)
