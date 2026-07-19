"""
Application entry point.

Runs the complete OCR Intelligence Engine pipeline.

Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import sys

import time

from pathlib import Path


from core.logger import logger


from config.settings import PATHS


from pipeline.analyzer import PDFAnalyzer

from pipeline.renderer import PDFRenderer

from pipeline.preprocess import ImagePreprocessor

from pipeline.layout import LayoutDetector

from pipeline.extractor import VisionExtractor

from pipeline.assembler import MarkdownAssembler

from pipeline.validator import DocumentValidator


from models.document import (
    PageExtraction,
    ExtractionResponse,
)



class OCRPipeline:
    """
    Complete document intelligence pipeline.
    """

    def __init__(self) -> None:

        logger.info(
            "Initializing OCR pipeline"
        )


        self.analyzer = PDFAnalyzer()

        self.renderer = PDFRenderer()

        self.preprocessor = ImagePreprocessor()

        self.layout_detector = LayoutDetector()

        self.extractor = VisionExtractor()

        self.assembler = MarkdownAssembler()

        self.validator = DocumentValidator()



    def run(
        self,
        pdf_path: Path,
    ) -> None:
        """
        Execute complete pipeline.

        Args:
            pdf_path:
                Input PDF.
        """

        start = time.perf_counter()


        logger.info(
            "Processing started: %s",
            pdf_path.name,
        )


        # ---------------------------------
        # 1. Analyze document
        # ---------------------------------

        metadata = (
            self.analyzer.analyze(
                pdf_path
            )
        )



        # ---------------------------------
        # 2. Render pages
        # ---------------------------------

        rendered_pages = (
            self.renderer.render_document(
                pdf_path,
                metadata,
            )
        )



        # ---------------------------------
        # 3. Extract page content
        # ---------------------------------

        page_results = []


        for rendered_page in rendered_pages:


            processed_page = (
                self.preprocessor.process(
                    rendered_page
                )
            )


            regions = (
                self.layout_detector.detect(
                    processed_page
                )
            )


            extraction_results = []


            for region in regions:


                result = (
                    self.extractor.extract(
                        processed_page.output_path,
                        region,
                    )
                )


                extraction_results.append(
                    result
                )



            page_results.append(

                PageExtraction(

                    page_number=
                    rendered_page.page_number,

                    regions=
                    extraction_results,

                )

            )



        # ---------------------------------
        # 4. Assemble Markdown
        # ---------------------------------

        document = (
            self.assembler.assemble(
                metadata,
                page_results,
            )
        )



        # ---------------------------------
        # 5. Validate
        # ---------------------------------

        validation = (
            self.validator.validate(
                document
            )
        )



        if not validation.passed:

            logger.warning(
                "Validation issues detected: %s",
                validation.issues,
            )



        # ---------------------------------
        # 6. Save output
        # ---------------------------------

        output_file = (
            PATHS.output
            /
            "document.md"
        )


        output_file.write_text(
            document.markdown,
            encoding="utf-8",
        )


        elapsed = (
            time.perf_counter()
            -
            start
        )


        logger.info(
            "Completed in %.2f seconds",
            elapsed,
        )


        logger.info(
            "Output saved: %s",
            output_file,
        )



def main() -> None:
    """
    CLI entry point.
    """

    if len(sys.argv) < 2:

        print(
            "Usage: python main.py <pdf_path>"
        )

        return



    pdf_path = Path(
        sys.argv[1]
    )


    pipeline = OCRPipeline()


    pipeline.run(
        pdf_path
    )



if __name__ == "__main__":

    main()