"""
Centralized logging system for OCR Intelligence Engine.

All modules must use this logger.

Never use print() for application events.

Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


from config.settings import PATHS


# ==========================================================
# CONSTANTS
# ==========================================================

LOGGER_NAME = "ocr_engine"

LOG_FILE_NAME = "ocr_engine.log"

MAX_LOG_SIZE = 10 * 1024 * 1024   # 10 MB

BACKUP_COUNT = 5


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"



# ==========================================================
# LOGGER FACTORY
# ==========================================================

def create_logger() -> logging.Logger:
    """
    Creates and configures application logger.

    Returns:
        Configured logger instance.
    """

    logger = logging.getLogger(LOGGER_NAME)


    # Prevent duplicate handlers
    if logger.handlers:
        return logger


    logger.setLevel(logging.INFO)



    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )


    # ------------------------------------------------------
    # Console Handler
    # ------------------------------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )


    logger.addHandler(
        console_handler
    )



    # ------------------------------------------------------
    # File Handler
    # ------------------------------------------------------

    log_directory: Path = PATHS.logs

    log_file = (
        log_directory /
        LOG_FILE_NAME
    )


    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )


    file_handler.setFormatter(
        formatter
    )


    logger.addHandler(
        file_handler
    )


    return logger



# ==========================================================
# GLOBAL LOGGER INSTANCE
# ==========================================================

logger = create_logger()