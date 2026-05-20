import logging


def get_logger() -> logging.Logger:
    """Return a module-level logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    return logging.getLogger()
