"""
Document Chunk Manager.

Creates retrieval optimized chunks
for RAG systems.


Responsibilities:

- Split documents intelligently
- Preserve metadata
- Maintain context overlap
- Support tables


Author:
    Your Name
"""

from __future__ import annotations


from dataclasses import dataclass, field


from typing import List


from core.logger import logger



@dataclass(slots=True)
class DocumentChunk:
    """
    RAG chunk representation.
    """

    chunk_id: str

    text: str

    metadata: dict = field(
        default_factory=dict
    )



class ChunkManager:
    """
    Intelligent document splitter.
    """

    def __init__(
        self,
        chunk_size: int = 800,

        overlap: int = 100,

    ):

        self.chunk_size = chunk_size

        self.overlap = overlap


        logger.info(
            "Chunk manager initialized"
        )



    def create_chunks(
        self,
        document_text: str,

        document_id: str,

        metadata: dict | None = None,

    ) -> List[DocumentChunk]:
        """
        Convert document into chunks.
        """

        if metadata is None:

            metadata = {}



        sections = self._split_sections(

            document_text

        )


        chunks = []


        counter = 1


        for section in sections:


            section_chunks = (
                self._split_text(
                    section
                )
            )


            for text in section_chunks:


                chunks.append(

                    DocumentChunk(

                        chunk_id=

                        f"{document_id}_{counter}",


                        text=text,


                        metadata={

                            "document_id":

                            document_id,


                            **metadata

                        }

                    )

                )


                counter += 1



        return chunks



    def _split_sections(
        self,
        text: str,
    ) -> list[str]:
        """
        Split markdown sections.

        Keeps headings together.
        """

        sections = text.split(

            "\n# "

        )


        return [

            section.strip()

            for section in sections

            if section.strip()

        ]



    def _split_text(
        self,
        text: str,
    ) -> list[str]:
        """
        Size controlled splitting.
        """

        words = text.split()


        chunks = []


        start = 0


        while start < len(words):


            end = (

                start

                +

                self.chunk_size

            )


            chunk_words = words[

                start:end

            ]


            chunks.append(

                " ".join(
                    chunk_words
                )

            )


            start = (

                end

                -

                self.overlap

            )


        return chunks