"""
Markdown document assembler.

Combines individual region extraction
results into a coherent document.

Responsible for:

- Ordering
- Context preservation
- Markdown generation
- Document memory


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


from core.logger import logger


from models.document import (
    PageExtraction,
    DocumentState,
    MarkdownDocument,
    DocumentMetadata,
)


from utils.helpers import execution_timer



class MarkdownAssembler:
    """
    Builds final markdown document.
    """

    def __init__(self) -> None:

        self.state = DocumentState()


        logger.info(
            "Markdown assembler initialized"
        )



    def assemble(
        self,
        metadata: DocumentMetadata,
        pages: list[PageExtraction],
    ) -> MarkdownDocument:
        """
        Combine page outputs.

        Args:
            metadata:
                Document metadata.

            pages:
                Page extraction results.

        Returns:
            Complete markdown document.
        """

        with execution_timer(
            "Markdown assembly"
        ):


            ordered_pages = sorted(
                pages,
                key=lambda x: x.page_number,
            )


            markdown_parts = []


            for page in ordered_pages:

                self.state.current_page = (
                    page.page_number
                )


                page_markdown = (
                    self._assemble_page(
                        page
                    )
                )


                markdown_parts.append(
                    page_markdown
                )


            final_markdown = (
                "\n\n"
                .join(markdown_parts)
            )


            document = MarkdownDocument(

                metadata=metadata,

                markdown=final_markdown,

                processing_time=0,

                warnings=self.state.warnings,

            )


            logger.info(
                "Document assembled successfully"
            )


            return document



    def _assemble_page(
        self,
        page: PageExtraction,
    ) -> str:
        """
        Assemble one page.
        """

        content = []


        regions = sorted(
            page.regions,
            key=lambda x: x.region_id,
        )


        for region in regions:

            markdown = (
                region.markdown
                .strip()
            )


            if not markdown:

                continue


            markdown = (
                self._update_state(
                    markdown
                )
            )


            content.append(
                markdown
            )


        return "\n\n".join(content)



    def _update_state(
        self,
        markdown: str,
    ) -> str:
        """
        Track document context.
        """

        if markdown.startswith("# "):

            self.state.current_h1 = (
                markdown[2:]
                .strip()
            )


        elif markdown.startswith("## "):

            self.state.current_h2 = (
                markdown[3:]
                .strip()
            )


        elif markdown.startswith("### "):

            self.state.current_h3 = (
                markdown[4:]
                .strip()
            )


        return markdown