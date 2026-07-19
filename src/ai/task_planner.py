"""
AI Task Planner.

Decides the optimal extraction
strategy for every document page.


Responsibilities:

- Classify page type
- Select processing strategy
- Optimize resource usage


Designed for:

- Small VLMs
- Low-end hardware
- Large PDFs


Author:
    Your Name
"""

from __future__ import annotations


from enum import Enum


from dataclasses import (
    dataclass,
    field,
)


from core.logger import logger



class PageType(str, Enum):
    """
    Document page categories.
    """

    TEXT = "text"

    TABLE = "table"

    IMAGE = "image"

    DIAGRAM = "diagram"

    MIXED = "mixed"

    UNKNOWN = "unknown"



class ProcessingStrategy(str, Enum):
    """
    Extraction pipeline choices.
    """

    OCR_ONLY = "ocr_only"

    VISION_ONLY = "vision_only"

    OCR_PLUS_VISION = "ocr_plus_vision"

    STRUCTURE_ANALYSIS = "structure_analysis"

    VERIFICATION_REQUIRED = "verification_required"



@dataclass(slots=True)
class PagePlan:
    """
    Processing instructions for one page.
    """

    page_number: int

    page_type: PageType

    strategy: list[ProcessingStrategy]

    confidence: float

    notes: list[str] = field(
        default_factory=list
    )



class TaskPlanner:
    """
    Intelligent document workflow planner.
    """

    def __init__(self):

        logger.info(
            "Task planner initialized"
        )



    def analyze_page(
        self,
        page_metadata: dict,
    ) -> PagePlan:
        """
        Decide processing strategy.
        """


        page_number = (
            page_metadata[
                "page_number"
            ]
        )


        text_density = (
            page_metadata.get(
                "text_density",
                0
            )
        )


        image_density = (
            page_metadata.get(
                "image_density",
                0
            )
        )


        table_probability = (
            page_metadata.get(
                "table_probability",
                0
            )
        )



        # ----------------------------
        # Table heavy page
        # ----------------------------

        if table_probability > 0.7:


            return PagePlan(

                page_number,

                PageType.TABLE,

                [

                    ProcessingStrategy.OCR_PLUS_VISION,

                    ProcessingStrategy.VERIFICATION_REQUIRED

                ],

                0.9,

                [

                    "Complex table detected"

                ]

            )



        # ----------------------------
        # Text page
        # ----------------------------

        if text_density > 0.7:


            return PagePlan(

                page_number,

                PageType.TEXT,

                [

                    ProcessingStrategy.OCR_ONLY

                ],

                0.85,

                [

                    "Mostly text page"

                ]

            )



        # ----------------------------
        # Image page
        # ----------------------------

        if image_density > 0.7:


            return PagePlan(

                page_number,

                PageType.IMAGE,

                [

                    ProcessingStrategy.VISION_ONLY

                ],

                0.85,

                [

                    "Visual content detected"

                ]

            )



        # ----------------------------
        # Mixed page
        # ----------------------------


        return PagePlan(

            page_number,

            PageType.MIXED,

            [

                ProcessingStrategy.OCR_PLUS_VISION

            ],

            0.6,

            [

                "Mixed content"

            ]

        )