"""Custom filters untuk logging."""


def streamlit_filter(record):
    """Filter noisy Streamlit internal logs."""
    # Skip Streamlit DEBUG/INFO yang tidak penting
    if record["name"].startswith("streamlit") and record["level"].name in {
        "DEBUG",
        "INFO",
    }:
        return False
    # Skip watchdog file change notifications
    if "watchdog" in record["name"].lower():
        return False
    return True


def error_filter(record):
    """Filter untuk separate error logs."""
    return record["level"].name != "ERROR"


def info_filter(record):
    """Filter untuk info-level logs."""
    return record["level"].name in {"INFO", "SUCCESS", "WARNING"}
