"""
PDF Document Analyzer.

Responsible for understanding the input document
before the processing pipeline begins.

Responsibilities:

- Validate PDF
- Extract metadata
- Detect document type
- Estimate complexity
- Recommend rendering DPI


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


from pathlib import Path

import fitz


from config.settings import RENDERING

from models.document import (
    DocumentMetadata,
    DocumentType,
    PageMetadata,
)

from core.logger import logger

from utils.helpers import (
    validate_file_exists,
    validate_pdf,
    execution_timer,
)



class PDFAnalyzer:
    """
    Analyzes PDF documents before OCR processing.
    """

    def __init__(self) -> None:
        """
        Initialize analyzer.
        """

        logger.info(
            "PDF Analyzer initialized"
        )


    def analyze(
        self,
        pdf_path: Path,
    ) -> DocumentMetadata:
        """
        Analyze PDF document.

        Args:
            pdf_path:
                Path to PDF.

        Returns:
            Document metadata.
        """

        with execution_timer(
            "PDF analysis"
        ):

            validate_file_exists(
                pdf_path
            )

            validate_pdf(
                pdf_path
            )


            logger.info(
                "Analyzing document: %s",
                pdf_path.name,
            )


            document = fitz.open(
                pdf_path
            )


            encrypted = document.is_encrypted


            pages = []

            scanned_pages = 0

            digital_pages = 0



            for index, page in enumerate(document):

                page_metadata = (
                    self._analyze_page(
                        page,
                        index + 1
                    )
                )


                pages.append(
                    page_metadata
                )


                if page_metadata.scanned:

                    scanned_pages += 1

                else:

                    digital_pages += 1



            document_type = (
                self._detect_document_type(
                    scanned_pages,
                    digital_pages,
                )
            )


            dpi = (
                self._recommend_dpi(
                    pages
                )
            )


            metadata = DocumentMetadata(

                filename=pdf_path.name,

                total_pages=len(document),

                document_type=document_type,

                encrypted=encrypted,

                file_size_bytes=(
                    pdf_path.stat()
                    .st_size
                ),

                recommended_dpi=dpi,

                estimated_runtime_seconds=(
                    self._estimate_runtime(
                        len(document)
                    )
                ),

                pages=pages,
            )


            document.close()


            logger.info(
                "Analysis completed. Pages: %s Type: %s",
                metadata.total_pages,
                metadata.document_type.value,
            )


            return metadata



    def _analyze_page(
        self,
        page: fitz.Page,
        page_number: int,
    ) -> PageMetadata:
        """
        Analyze individual PDF page.
        """

        text = (
            page.get_text()
            .strip()
        )


        scanned = (
            len(text)
            <
            20
        )


        rectangle = page.rect


        return PageMetadata(

            page_number=page_number,

            width=rectangle.width,

            height=rectangle.height,

            rotation=page.rotation,

            dpi=RENDERING.default_dpi,

            scanned=scanned,

        )



    def _detect_document_type(
        self,
        scanned_pages: int,
        digital_pages: int,
    ) -> DocumentType:
        """
        Classify PDF type.
        """

        if scanned_pages == 0:

            return DocumentType.DIGITAL


        if digital_pages == 0:

            return DocumentType.SCANNED


        return DocumentType.HYBRID



    def _recommend_dpi(
        self,
        pages: list[PageMetadata],
    ) -> int:
        """
        Select rendering resolution.
        """

        scanned_count = sum(
            1
            for page in pages
            if page.scanned
        )


        if scanned_count == 0:

            return RENDERING.minimum_dpi


        if scanned_count > 10:

            return RENDERING.maximum_dpi


        return RENDERING.default_dpi



    def _estimate_runtime(
        self,
        pages: int,
    ) -> float:
        """
        Rough processing estimate.

        Later replaced by learned metrics.
        """

        seconds_per_page = 15

        return (
            pages
            *
            seconds_per_page
        )