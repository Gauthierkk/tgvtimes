"""Centralized logging configuration for TGV Times application.

This module provides a standardized logger with consistent formatting across
all modules in the application.
"""

import logging
import sys
from pathlib import Path


class LoggerConfig:
    """Configure and manage application logging."""

    # Default log format with aligned fields including pathname and function
    LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Log file location
    LOG_DIR = Path(__file__).parent.parent.parent  # Project root
    LOG_FILE = LOG_DIR / "tgvtimes.log"

    _configured = False

    @classmethod
    def configure(cls, level: int = logging.INFO) -> None:
        """
        Configure the root logger with standardized formatting.

        Args:
            level: Logging level (default: INFO)
        """
        if cls._configured:
            return

        # Create formatter with aligned fields
        formatter = logging.Formatter(
            fmt=cls.LOG_FORMAT,
            datefmt=cls.DATE_FORMAT
        )

        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        # File handler
        file_handler = logging.FileHandler(cls.LOG_FILE, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture all levels
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        cls._configured = True


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger for a module.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Minimum logging level for console output (default: INFO)

    Returns:
        Configured logger instance

    Example:
        >>> from data import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
        >>> logger.debug("Detailed debug information")
    """
    # Configure logging on first use
    LoggerConfig.configure(level=level)

    # Return logger for the specified module
    logger = logging.getLogger(name)
    return logger
