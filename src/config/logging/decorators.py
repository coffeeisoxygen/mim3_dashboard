"""Enhanced decorators dengan consistent API."""

import functools
import time
from collections.abc import Callable
from typing import Any

from loguru import logger


@logger.catch(reraise=True)
def log_performance(operation: str, *, min_duration: float = 0.1, level: str = "INFO"):
    """Universal performance logging decorator."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.time()

            # Context for all logs in this function
            with logger.contextualize(
                operation=operation,
                function=func.__name__,
                module=func.__module__,
            ):
                try:
                    logger.debug(f"🚀 Starting {operation}")
                    result = func(*args, **kwargs)
                    duration = time.time() - start

                    # Only log if duration exceeds threshold
                    if duration >= min_duration:
                        logger.log(
                            level,
                            f"⚡ {operation} completed",
                            duration=f"{duration:.3f}s",
                        )

                    return result

                except Exception as e:
                    duration = time.time() - start
                    logger.error(
                        f"💥 {operation} failed",
                        duration=f"{duration:.3f}s",
                        error_type=type(e).__name__,
                        error_msg=str(e),
                    )
                    raise

        return wrapper

    return decorator


# Alias untuk backward compatibility
def log_performance_legacy(func_name: str):
    """Legacy decorator - use log_performance instead."""
    return log_performance(func_name, min_duration=0.0)
