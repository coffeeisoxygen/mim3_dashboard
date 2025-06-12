"""Custom handlers untuk logging integration."""

import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """Redirect standard logging ke Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Redirect log messages to Loguru.

        This method is called for each log message. It translates the standard logging
        levels to Loguru levels and forwards the message to the Loguru logger.

        Args:
            record (logging.LogRecord): The log record containing the message and metadata.
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions."""
    if not issubclass(exc_type, KeyboardInterrupt):
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical(
            "Uncaught exception"
        )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def get_logger(name: str | None = None):
    """Get logger dengan optional module context."""
    if name:
        return logger.bind(module=name)
    return logger
