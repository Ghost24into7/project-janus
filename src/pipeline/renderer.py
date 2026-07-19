"""
PDF rendering engine.

Converts PDF pages into optimized images
for vision models.

Responsibilities:

- Page rendering
- DPI control
- Memory-safe processing
- Image caching


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


from pathlib import Path


import fitz


from config.settings import (
    PATHS,
    RENDERING,
)

from models.document import (
    DocumentMetadata,
    RenderedPage,
)

from core.logger import logger

from utils.helpers import (
    ensure_directory,
    execution_timer,
)



class PDFRenderer:
    """
    Responsible for PDF page rendering.
    """

    def __init__(self) -> None:
        """
        Initialize renderer.
        """

        self.output_directory = ensure_directory(
            PATHS.temp / "rendered_pages"
        )


        logger.info(
            "PDF Renderer initialized"
        )



    def render_page(
        self,
        pdf_path: Path,
        page_number: int,
        dpi: int | None = None,
    ) -> RenderedPage:
        """
        Render a single PDF page.

        Only one page exists in memory.

        Args:
            pdf_path:
                PDF location.

            page_number:
                Page index starting from 1.

            dpi:
                Rendering resolution.

        Returns:
            RenderedPage object.
        """

        with execution_timer(
            f"Rendering page {page_number}"
        ):


            selected_dpi = (
                dpi
                or
                RENDERING.default_dpi
            )


            document = fitz.open(
                pdf_path
            )


            page = document.load_page(
                page_number - 1
            )


            scale = (
                selected_dpi
                /
                72
            )


            matrix = fitz.Matrix(
                scale,
                scale,
            )


            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )


            output_path = (
                self.output_directory
                /
                f"page_{page_number}.png"
            )


            pixmap.save(
                output_path
            )


            rendered_page = RenderedPage(

                page_number=page_number,

                image_path=output_path,

                width=pixmap.width,

                height=pixmap.height,

                dpi=selected_dpi,
            )


            document.close()


            logger.info(
                "Rendered page %s",
                page_number,
            )


            return rendered_page



    def render_document(
        self,
        pdf_path: Path,
        metadata: DocumentMetadata,
    ) -> list[RenderedPage]:
        """
        Render complete document.

        Note:
        This returns paths, not images.

        Images stay on disk.

        """

        rendered_pages = []


        for page in metadata.pages:

            rendered = self.render_page(

                pdf_path,

                page.page_number,

                metadata.recommended_dpi,

            )


            rendered_pages.append(
                rendered
            )


        return rendered_pages