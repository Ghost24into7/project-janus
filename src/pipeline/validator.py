"""
Document quality validation engine.

Checks the generated markdown before
final delivery.

Responsibilities:

- Content coverage
- Markdown validation
- Confidence checks
- Quality scoring


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import re


from core.logger import logger


from models.document import (
    MarkdownDocument,
    ValidationResult,
)


from utils.helpers import execution_timer



class DocumentValidator:
    """
    Validates final extracted documents.
    """

    def __init__(
        self,
        minimum_score: float = 0.75,
    ) -> None:

        self.minimum_score = (
            minimum_score
        )


        logger.info(
            "Document validator initialized"
        )



    def validate(
        self,
        document: MarkdownDocument,
    ) -> ValidationResult:
        """
        Validate markdown output.

        Args:
            document:
                Final markdown document.

        Returns:
            Validation result.
        """

        with execution_timer(
            "Document validation"
        ):


            issues = []


            score_parts = []



            coverage_score = (
                self._check_content(
                    document,
                    issues,
                )
            )


            markdown_score = (
                self._check_markdown(
                    document.markdown,
                    issues,
                )
            )


            warning_score = (
                self._check_warnings(
                    document,
                    issues,
                )
            )


            score_parts.extend(

                [

                    coverage_score,

                    markdown_score,

                    warning_score,

                ]

            )


            final_score = (
                sum(score_parts)
                /
                len(score_parts)
            )


            passed = (
                final_score
                >=
                self.minimum_score
            )


            result = ValidationResult(

                passed=passed,

                score=round(
                    final_score,
                    2
                ),

                issues=issues,

            )


            if passed:

                logger.info(
                    "Validation passed score=%s",
                    result.score,
                )

            else:

                logger.warning(
                    "Validation failed score=%s",
                    result.score,
                )


            return result



    def _check_content(
        self,
        document: MarkdownDocument,
        issues: list[str],
    ) -> float:
        """
        Check content existence.
        """

        if not document.markdown.strip():

            issues.append(
                "Document contains no markdown"
            )

            return 0.0


        length = len(
            document.markdown
        )


        if length < 100:

            issues.append(
                "Very small extracted content"
            )

            return 0.5


        return 1.0



    def _check_markdown(
        self,
        markdown: str,
        issues: list[str],
    ) -> float:
        """
        Basic markdown validation.
        """

        score = 1.0


        # Detect broken tables

        table_lines = [
            line
            for line in markdown.splitlines()
            if "|" in line
        ]


        for line in table_lines:

            columns = (
                line.count("|")
            )


            if columns < 2:

                issues.append(
                    "Possible broken table"
                )

                score -= 0.1



        # Detect excessive whitespace

        if re.search(
            r"\n{5,}",
            markdown,
        ):

            issues.append(
                "Excessive empty lines"
            )

            score -= 0.1



        return max(
            score,
            0,
        )



    def _check_warnings(
        self,
        document: MarkdownDocument,
        issues: list[str],
    ) -> float:
        """
        Check pipeline warnings.
        """

        warning_count = len(
            document.warnings
        )


        if warning_count == 0:

            return 1.0


        issues.extend(
            document.warnings
        )


        penalty = (
            warning_count
            *
            0.1
        )


        return max(
            1.0 - penalty,
            0,
        )