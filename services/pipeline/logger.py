import logging

LOG_FORMAT = "{asctime} - {levelname} - {name} - {message}"
LOG_DATEFMT = "%Y-%m-%d %H:%M"


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)


def configure_logging() -> None:
    """Configure root logging. Call once from the entrypoint."""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        style="{",
        datefmt=LOG_DATEFMT,
    )
