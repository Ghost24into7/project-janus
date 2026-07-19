"""
AI Model Router.

Selects the correct AI component
for each document task.

Responsibilities:

- Route tasks
- Optimize hardware usage
- Reduce unnecessary VLM calls
- Support multiple AI models


Author:
    Your Name
"""

from __future__ import annotations


from enum import Enum


from dataclasses import dataclass


from core.logger import logger



class AIComponent(str, Enum):
    """
    Available processing engines.
    """

    PADDLE_OCR = "paddleocr"

    TESSERACT = "tesseract"

    QWEN_VL = "qwen3-vl"

    VALIDATOR = "validator"



@dataclass(slots=True)
class RoutingDecision:
    """
    Routing result.
    """

    primary_model: AIComponent

    secondary_models: list[AIComponent]

    reason: str

    expected_latency: str



class AIRouter:
    """
    Intelligent AI execution router.
    """

    def __init__(self):

        logger.info(
            "AI router initialized"
        )



    def route(
        self,
        page_plan,
    ) -> RoutingDecision:
        """
        Decide processing pipeline.
        """



        page_type = (
            page_plan.page_type
        )


        strategy = (
            page_plan.strategy
        )



        # ----------------------------
        # Text pages
        # ----------------------------

        if page_type.value == "text":


            return RoutingDecision(

                primary_model=
                AIComponent.PADDLE_OCR,


                secondary_models=[],

                reason=
                "Simple text extraction",


                expected_latency=
                "fast"

            )



        # ----------------------------
        # Tables
        # ----------------------------

        if page_type.value == "table":


            return RoutingDecision(

                primary_model=
                AIComponent.PADDLE_OCR,


                secondary_models=[

                    AIComponent.QWEN_VL,

                    AIComponent.VALIDATOR

                ],

                reason=
                "Tables require visual understanding",


                expected_latency=
                "medium"

            )



        # ----------------------------
        # Images / diagrams
        # ----------------------------

        if page_type.value in [

            "image",

            "diagram"

        ]:


            return RoutingDecision(

                primary_model=
                AIComponent.QWEN_VL,


                secondary_models=[

                    AIComponent.VALIDATOR

                ],


                reason=
                "Requires visual reasoning",


                expected_latency=
                "slow"

            )



        # ----------------------------
        # Mixed documents
        # ----------------------------


        return RoutingDecision(

            primary_model=
            AIComponent.PADDLE_OCR,


            secondary_models=[

                AIComponent.QWEN_VL

            ],


            reason=
            "Mixed content requires hybrid approach",


            expected_latency=
            "medium"

        )