"""
Image preprocessing engine.

Responsible for preparing rendered PDF pages
for vision models.

Uses OpenCV for image enhancement.

Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


from pathlib import Path


import cv2
import numpy as np


from config.settings import PATHS

from core.logger import logger

from models.document import (
    RenderedPage,
    ProcessedPage,
    ImageQuality,
)

from utils.helpers import (
    ensure_directory,
    execution_timer,
)



class ImagePreprocessor:
    """
    Enhances images before AI extraction.
    """

    def __init__(self) -> None:

        self.output_directory = ensure_directory(
            PATHS.temp / "processed_pages"
        )


        logger.info(
            "Image preprocessor initialized"
        )


    def process(
        self,
        page: RenderedPage,
    ) -> ProcessedPage:
        """
        Process one rendered page.

        Args:
            page:
                Rendered PDF page.

        Returns:
            Processed page.
        """

        with execution_timer(
            f"Preprocessing page {page.page_number}"
        ):

            image = self._load_image(
                page.image_path
            )


            quality = self._analyze_quality(
                image
            )


            image = self._correct_orientation(
                image
            )


            image = self._deskew(
                image
            )


            image = self._remove_noise(
                image
            )


            image = self._enhance_contrast(
                image
            )


            image = self._remove_border(
                image
            )


            output_path = (
                self.output_directory
                /
                f"processed_{page.page_number}.png"
            )


            cv2.imwrite(
                str(output_path),
                image,
            )


            logger.info(
                "Processed page %s Quality %.2f",
                page.page_number,
                quality.quality_score,
            )


            return ProcessedPage(

                page_number=page.page_number,

                input_path=page.image_path,

                output_path=output_path,

                quality=quality,
            )



    def _load_image(
        self,
        path: Path,
    ) -> np.ndarray:
        """
        Load image.
        """

        image = cv2.imread(
            str(path)
        )


        if image is None:

            raise ValueError(
                f"Unable to load image {path}"
            )


        return image



    def _analyze_quality(
        self,
        image: np.ndarray,
    ) -> ImageQuality:
        """
        Estimate image quality.
        """

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )


        brightness = float(
            np.mean(gray)
        )


        sharpness = float(
            cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()
        )


        noise = float(
            np.std(gray)
        )


        quality = min(
            100,
            (
                sharpness / 100
                +
                brightness / 255 * 50
            )
        )


        return ImageQuality(

            width=image.shape[1],

            height=image.shape[0],

            brightness=brightness,

            sharpness=sharpness,

            noise_score=noise,

            quality_score=quality,

        )



    def _correct_orientation(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Placeholder for orientation model.

        Future:
        Use OCR orientation classifier.
        """

        return image



    def _deskew(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Correct rotated text.
        """

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )


        coords = np.column_stack(
            np.where(
                gray < 255
            )
        )


        if len(coords) < 20:

            return image


        angle = cv2.minAreaRect(
            coords
        )[-1]


        if angle < -45:

            angle = -(90 + angle)

        else:

            angle = -angle



        height, width = gray.shape


        center = (
            width // 2,
            height // 2
        )


        matrix = cv2.getRotationMatrix2D(
            center,
            angle,
            1.0,
        )


        return cv2.warpAffine(
            image,
            matrix,
            (width, height),
            borderMode=cv2.BORDER_REPLICATE,
        )



    def _remove_noise(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        return cv2.fastNlMeansDenoisingColored(
            image,
            None,
            10,
            10,
            7,
            21,
        )



    def _enhance_contrast(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        lab = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2LAB,
        )


        l, a, b = cv2.split(
            lab
        )


        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8,8),
        )


        enhanced_l = clahe.apply(
            l
        )


        merged = cv2.merge(
            (
                enhanced_l,
                a,
                b,
            )
        )


        return cv2.cvtColor(
            merged,
            cv2.COLOR_LAB2BGR,
        )



    def _remove_border(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Remove scanning borders.

        Conservative implementation.
        """

        height, width = image.shape[:2]


        margin_x = int(
            width * 0.02
        )

        margin_y = int(
            height * 0.02
        )


        return image[
            margin_y:height-margin_y,
            margin_x:width-margin_x
        ]