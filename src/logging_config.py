import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from colorlog import ColoredFormatter


def setup_logging():
    logger = logging.getLogger("LuminaSync")
    # Set loglevel based on DEBUG environment variable
    loglevel = logging.DEBUG if "DEBUG" in os.environ else logging.INFO

    logger.setLevel(loglevel)

    if not logger.handlers:
        file_handler = RotatingFileHandler(
            "logs/luminasync.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,  # Keep up to 5 backup files
        )
        file_handler.setLevel(loglevel)

        # Define a formatter for the file handler
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s -  %(name)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)

        # Create a console handler for logging to the console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(loglevel)

        # Define a colored formatter for the console handler
        console_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        console_handler.setFormatter(console_formatter)

        # Add both handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.info("Logging is set up.")


def get_logger(cls):
    """
    Helper function to get a child logger for a class.
    """
    logger = logging.getLogger("LuminaSync")
    return logger.getChild(cls.__name__)
