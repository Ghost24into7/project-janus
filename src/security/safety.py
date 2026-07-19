"""
Security and safety validation layer.

Protects document AI pipeline
from unsafe inputs.

Responsibilities:

- File validation
- Size restrictions
- Filename sanitization
- Basic threat detection


Author:
    Your Name

Python:
    3.12+
"""

from __future__ import annotations


import re

from pathlib import Path


from dataclasses import dataclass


from core.logger import logger



@dataclass(slots=True)
class SafetyResult:
    """
    Security validation result.
    """

    allowed: bool

    reason: str | None = None



class DocumentSafetyManager:
    """
    Validates incoming documents.
    """

    def __init__(
        self,
        max_file_size_mb: int = 100,
        max_pages: int = 500,
    ):

        self.max_file_size_mb = (
            max_file_size_mb
        )

        self.max_pages = (
            max_pages
        )


        logger.info(
            "Safety manager initialized"
        )



    def validate_file(
        self,
        file_path: Path,
    ) -> SafetyResult:
        """
        Perform security checks.
        """

        checks = [

            self._check_extension(
                file_path
            ),

            self._check_size(
                file_path
            ),

            self._check_filename(
                file_path
            ),

        ]


        for result in checks:

            if not result.allowed:

                logger.warning(
                    "Security blocked file: %s",
                    result.reason,
                )

                return result



        return SafetyResult(
            allowed=True
        )



    def _check_extension(
        self,
        file_path: Path,
    ) -> SafetyResult:
        """
        Allow only PDF.
        """

        if file_path.suffix.lower() != ".pdf":

            return SafetyResult(

                False,

                "Unsupported file type"

            )


        return SafetyResult(
            True
        )



    def _check_size(
        self,
        file_path: Path,
    ) -> SafetyResult:
        """
        Check file size.
        """

        size_mb = (

            file_path.stat().st_size

            /

            (1024 * 1024)

        )


        if size_mb > self.max_file_size_mb:

            return SafetyResult(

                False,

                f"File exceeds {self.max_file_size_mb}MB limit"

            )


        return SafetyResult(
            True
        )



    def _check_filename(
        self,
        file_path: Path,
    ) -> SafetyResult:
        """
        Prevent unsafe filenames.
        """

        filename = file_path.name


        if re.search(
            r"[<>:\"/\\|?*]",
            filename
        ):

            return SafetyResult(

                False,

                "Unsafe filename"

            )


        return SafetyResult(
            True
        )



    def sanitize_text(
        self,
        text: str,
    ) -> str:
        """
        Remove suspicious AI instructions.

        Note:

        This does NOT modify document meaning.
        It only reduces accidental instruction
        following.
        """

        patterns = [

            r"ignore previous instructions",

            r"system message",

            r"developer message",

            r"reveal prompt",

        ]


        cleaned = text


        for pattern in patterns:

            cleaned = re.sub(

                pattern,

                "[FILTERED]",

                cleaned,

                flags=re.IGNORECASE,

            )


        return cleaned