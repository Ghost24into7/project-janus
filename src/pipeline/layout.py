"""
Document layout detection engine.

Responsible for identifying semantic regions
inside document pages.

Current implementation:
    OpenCV based heuristic detector.

Future implementations:
    DocLayout-YOLO
    Surya
    RT-DETR


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


from pathlib import Path


import cv2


from core.logger import logger


from models.document import (
    BoundingBox,
    LayoutRegion,
    RegionType,
    ProcessedPage,
)


from utils.helpers import execution_timer



class LayoutDetector:
    """
    Detects document structure.
    """

    def __init__(self) -> None:

        logger.info(
            "Layout detector initialized"
        )


    def detect(
        self,
        page: ProcessedPage,
    ) -> list[LayoutRegion]:
        """
        Detect regions from processed page.

        Args:
            page:
                Enhanced page image.

        Returns:
            Detected layout regions.
        """

        with execution_timer(
            f"Layout detection page {page.page_number}"
        ):

            image = cv2.imread(
                str(page.output_path)
            )


            if image is None:

                raise ValueError(
                    f"Cannot load {page.output_path}"
                )


            regions = self._detect_blocks(
                image,
                page.page_number,
            )


            logger.info(
                "Detected %s regions on page %s",
                len(regions),
                page.page_number,
            )


            return regions



    def _detect_blocks(
        self,
        image,
        page_number: int,
    ) -> list[LayoutRegion]:
        """
        Basic document block detection.

        Uses contours.

        This is intentionally simple.
        Later replaced by ML detector.
        """

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )


        threshold = cv2.threshold(
            gray,
            200,
            255,
            cv2.THRESH_BINARY_INV,
        )[1]


        contours, _ = cv2.findContours(
            threshold,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )


        regions = []


        region_id = 1


        for contour in contours:

            x, y, width, height = cv2.boundingRect(
                contour
            )


            area = width * height


            # Ignore tiny noise
            if area < 500:

                continue



            region_type = self._classify_region(
                width,
                height,
                image.shape[1],
                image.shape[0],
            )


            regions.append(

                LayoutRegion(

                    id=region_id,

                    region_type=region_type,

                    bbox=BoundingBox(

                        x=x,

                        y=y,

                        width=width,

                        height=height,

                    ),

                    confidence=0.5,

                    page_number=page_number,

                    reading_order=region_id,

                )

            )


            region_id += 1



        return sorted(
            regions,
            key=lambda x: (
                x.bbox.y,
                x.bbox.x
            )
        )



    def _classify_region(
        self,
        width: int,
        height: int,
        page_width: int,
        page_height: int,
    ) -> RegionType:
        """
        Basic region classification.

        Placeholder until ML layout model.
        """

        relative_width = (
            width / page_width
        )


        relative_height = (
            height / page_height
        )


        # Large horizontal blocks
        if (
            relative_width > 0.8
            and relative_height < 0.1
        ):

            return RegionType.HEADING



        # Very wide regions
        if (
            relative_width > 0.7
            and height < 400
        ):

            return RegionType.PARAGRAPH



        # Square-ish large blocks
        if (
            abs(width-height) < 100
            and width > 300
        ):

            return RegionType.IMAGE



        return RegionType.UNKNOWN