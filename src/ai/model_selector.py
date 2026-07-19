"""
Adaptive AI model selector.

Chooses the best available model
based on:

- Hardware capacity
- Document complexity
- Accuracy requirements


Designed for local AI deployments.

Author:
    Your Name
"""

from __future__ import annotations


from dataclasses import dataclass


from enum import Enum


from core.logger import logger



class ModelCapability(str, Enum):

    TEXT = "text"

    VISION = "vision"

    REASONING = "reasoning"



@dataclass(slots=True)
class ModelProfile:
    """
    AI model information.
    """

    name: str

    capability: ModelCapability

    ram_required_gb: float

    quality_score: float

    speed_score: float



@dataclass(slots=True)
class SelectionResult:
    """
    Selected model output.
    """

    model_name: str

    reason: str

    confidence: float



class ModelSelector:
    """
    Dynamically selects models.
    """

    def __init__(self):

        self.models = [

            ModelProfile(

                name="qwen3-vl:4b",

                capability=
                ModelCapability.VISION,

                ram_required_gb=8,

                quality_score=0.85,

                speed_score=0.90,

            ),


            ModelProfile(

                name="qwen3-vl:8b",

                capability=
                ModelCapability.VISION,

                ram_required_gb=16,

                quality_score=0.92,

                speed_score=0.65,

            ),


            ModelProfile(

                name="llava:7b",

                capability=
                ModelCapability.VISION,

                ram_required_gb=12,

                quality_score=0.80,

                speed_score=0.70,

            )

        ]


        logger.info(
            "Model selector initialized"
        )



    def select(
        self,
        capability: ModelCapability,
        available_ram_gb: float,
        complexity: float,
    ) -> SelectionResult:
        """
        Select optimal model.
        """

        candidates = []


        for model in self.models:


            if model.capability != capability:

                continue


            if (
                model.ram_required_gb
                <=
                available_ram_gb
            ):

                candidates.append(
                    model
                )



        if not candidates:


            raise RuntimeError(
                "No compatible model available"
            )



        # Complexity aware scoring

        best = max(

            candidates,

            key=lambda m:

            (
                m.quality_score
                *
                complexity

                +

                m.speed_score
                *
                (1-complexity)

            )

        )


        return SelectionResult(

            model_name=best.name,

            reason=(

                f"Selected {best.name} "
                f"for complexity {complexity}"

            ),

            confidence=0.9

        )