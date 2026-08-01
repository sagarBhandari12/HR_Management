import logging
import sys

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configures application-wide logging with log level based on environment."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("hr_api")
    logger.setLevel(log_level)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger


logger = setup_logging()
