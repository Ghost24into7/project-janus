"""
AI document evaluation engine.

Measures extraction quality and
pipeline performance.

Responsibilities:

- Completeness scoring
- Structural validation
- Confidence aggregation
- Quality reporting


Author:
    Your Name

Python:
    3.12+
"""

from __future__ import annotations


import time

import re


from dataclasses import dataclass, field


from core.logger import logger



@dataclass(slots=True)
class EvaluationResult:
    """
    Evaluation output.
    """

    quality_score: float

    completeness_score: float

    structure_score: float

    confidence_score: float

    issues: list[str] = field(
        default_factory=list
    )

    processing_time: float = 0.0



class DocumentEvaluator:
    """
    Evaluates extracted documents.
    """

    def __init__(self):

        logger.info(
            "Evaluator initialized"
        )



    def evaluate(
        self,
        markdown: str,
        confidence_values: list[float] | None = None,
        start_time: float | None = None,
    ) -> EvaluationResult:
        """
        Run complete evaluation.
        """

        issues = []


        completeness = (
            self._calculate_completeness(
                markdown,
                issues
            )
        )


        structure = (
            self._evaluate_structure(
                markdown,
                issues
            )
        )


        confidence = (
            self._evaluate_confidence(
                confidence_values
            )
        )


        quality = (

            completeness

            *

            structure

            *

            confidence

        )


        processing_time = 0


        if start_time:

            processing_time = (

                time.perf_counter()

                -

                start_time

            )



        result = EvaluationResult(

            quality_score=
            round(
                quality,
                3
            ),

            completeness_score=
            completeness,

            structure_score=
            structure,

            confidence_score=
            confidence,

            issues=issues,

            processing_time=
            processing_time,

        )


        logger.info(

            "Document quality score %s",

            result.quality_score

        )


        return result



    def _calculate_completeness(
        self,
        markdown: str,
        issues: list[str],
    ) -> float:
        """
        Estimate content completeness.
        """

        if not markdown.strip():

            issues.append(
                "No extracted content"
            )

            return 0.0



        length = len(
            markdown
        )


        if length < 200:

            issues.append(
                "Very low extracted content"
            )

            return 0.5



        return 1.0



    def _evaluate_structure(
        self,
        markdown: str,
        issues: list[str],
    ) -> float:
        """
        Check markdown quality.
        """

        score = 1.0



        headings = len(

            re.findall(

                r"^#",

                markdown,

                re.MULTILINE

            )

        )



        if headings == 0:

            issues.append(
                "No headings detected"
            )

            score -= 0.2



        tables = markdown.count(
            "|"
        )


        if tables % 2 != 0:

            issues.append(
                "Possible broken table"
            )

            score -= 0.1



        return max(
            score,
            0
        )



    def _evaluate_confidence(
        self,
        values,
    ) -> float:
        """
        Calculate average confidence.
        """

        if not values:

            return 0.8


        return round(

            sum(values)

            /

            len(values),

            3

        )