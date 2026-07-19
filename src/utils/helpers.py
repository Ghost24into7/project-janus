"""
Common reusable utilities for OCR Intelligence Engine.

This module contains generic helper functions only.

No business logic belongs here.

Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import hashlib
import time
import shutil

from pathlib import Path

from contextlib import contextmanager
from typing import Generator


import psutil



from core.logger import logger



# ==========================================================
# FILE UTILITIES
# ==========================================================


def validate_file_exists(
    file_path: Path,
) -> None:
    """
    Validate that a file exists.

    Args:
        file_path:
            File location.

    Raises:
        FileNotFoundError:
            If file does not exist.
    """

    if not file_path.exists():

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )



def validate_pdf(
    file_path: Path,
) -> None:
    """
    Validate PDF extension.

    Args:
        file_path:
            Input file.

    Raises:
        ValueError:
            If not PDF.
    """

    if file_path.suffix.lower() != ".pdf":

        raise ValueError(
            "Only PDF files are supported."
        )



def ensure_directory(
    directory: Path,
) -> Path:
    """
    Create directory if missing.

    Args:
        directory:
            Directory path.

    Returns:
        Created directory path.
    """

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory



# ==========================================================
# HASHING
# ==========================================================


def calculate_file_hash(
    file_path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Calculate SHA256 hash of a file.

    Used for caching and duplicate detection.

    Args:
        file_path:
            File location.

        chunk_size:
            Reading chunk size.

    Returns:
        SHA256 hash string.
    """

    sha256 = hashlib.sha256()


    with file_path.open(
        "rb"
    ) as file:

        while chunk := file.read(chunk_size):

            sha256.update(
                chunk
            )


    return sha256.hexdigest()



# ==========================================================
# TIMING
# ==========================================================


@contextmanager
def execution_timer(
    operation: str,
) -> Generator[None, None, None]:
    """
    Measure execution time.

    Example:

        with execution_timer("PDF analysis"):
            analyze()

    """

    start = time.perf_counter()


    try:

        yield


    finally:

        elapsed = (
            time.perf_counter()
            -
            start
        )


        logger.info(
            "%s completed in %.2f seconds",
            operation,
            elapsed,
        )



# ==========================================================
# MEMORY UTILITIES
# ==========================================================


def get_memory_usage_mb() -> float:
    """
    Get current RAM usage.

    Returns:
        Memory usage in MB.
    """

    process = psutil.Process()

    memory_bytes = (
        process.memory_info()
        .rss
    )


    return (
        memory_bytes
        /
        (1024 ** 2)
    )



def check_available_memory_mb() -> float:
    """
    Get available system RAM.

    Returns:
        Available memory MB.
    """

    memory = psutil.virtual_memory()


    return (
        memory.available
        /
        (1024 ** 2)
    )



# ==========================================================
# IMAGE CACHE UTILITIES
# ==========================================================


def clear_directory(
    directory: Path,
) -> None:
    """
    Remove all contents inside directory.

    Used for temporary files.

    """

    if not directory.exists():

        return


    for item in directory.iterdir():

        if item.is_file():

            item.unlink()


        elif item.is_dir():

            shutil.rmtree(
                item
            )


    logger.info(
        "Cleared directory %s",
        directory,
    )