"""
Vision extraction engine.

Connects local vision models with
document regions.

Current backend:
    Ollama + Qwen3-VL

Future backends:
    vLLM
    TensorRT
    OpenAI-compatible APIs


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import time

from pathlib import Path


import ollama


from config.settings import MODEL

from core.logger import logger


from models.document import (
    LayoutRegion,
    ExtractionResponse,
)


from utils.helpers import execution_timer



class VisionExtractor:
    """
    Extracts document content using vision models.
    """

    def __init__(
        self,
    ) -> None:

        self.model_name = MODEL.model_name

        self.host = MODEL.host


        logger.info(
            "Vision extractor initialized using %s",
            self.model_name,
        )



    def extract(
        self,
        image_path: Path,
        region: LayoutRegion,
    ) -> ExtractionResponse:
        """
        Extract markdown from document region.

        Args:
            image_path:
                Processed image.

            region:
                Layout region.

        Returns:
            Extraction response.
        """

        start = time.perf_counter()


        prompt = self._build_prompt(
            region.region_type.value
        )


        try:

            response = ollama.chat(

                model=self.model_name,

                messages=[

                    {
                        "role": "user",

                        "content": prompt,

                        "images": [
                            str(image_path)
                        ],

                    }

                ],

            )


            markdown = (
                response
                .message
                .content
            )


            confidence = (
                self._estimate_confidence(
                    markdown
                )
            )


            elapsed = (
                time.perf_counter()
                -
                start
            )


            return ExtractionResponse(

                region_id=region.id,

                markdown=markdown,

                confidence=confidence,

                tokens_used=0,

                processing_time=elapsed,

            )


        except Exception as exc:

            logger.exception(
                "Vision extraction failed"
            )


            raise RuntimeError(
                "Qwen extraction failed"
            ) from exc



    def _build_prompt(
        self,
        region_type: str,
    ) -> str:
        """
        Generate specialized prompts.
        """

        prompts = {


            "title":
            """
            Extract the title.
            Return only markdown heading.
            Use # syntax.
            """,


            "table":
            """
            Extract this table.

            Rules:
            - Preserve rows
            - Preserve columns
            - Output markdown table
            - Do not summarize
            """,


            "paragraph":
            """
            Extract text exactly.

            Preserve:
            - paragraphs
            - lists
            - formatting
            """,


            "image":
            """
            Describe the image.

            Include:
            - what it shows
            - labels
            - important details
            """,

        }


        return prompts.get(
            region_type,
            """
            Extract all visible information.

            Return clean markdown.
            """
        )



    def _estimate_confidence(
        self,
        markdown: str,
    ) -> float:
        """
        Simple confidence estimation.

        Later replaced by:
        - model confidence
        - OCR comparison
        - validation model
        """

        if not markdown:

            return 0.0


        length_score = min(
            len(markdown) / 500,
            1.0
        )


        return round(
            length_score,
            2
        )