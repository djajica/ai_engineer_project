import logging

from .config import Settings

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging(settings: Settings | None = None) -> None:
    """Configure minimal structured logging for the app."""

    level_name = (settings.log_level if settings else "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=DATE_FORMAT)
