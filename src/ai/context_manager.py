"""
Context management system.

Provides external memory for
small vision language models.

Designed for:

- Qwen3-VL-4B
- Long PDFs
- Multi-page documents


Responsibilities:

- Maintain document memory
- Summarize previous pages
- Track entities
- Build model context


Author:
    Your Name
"""

from __future__ import annotations


from dataclasses import (
    dataclass,
    field,
)


from collections import defaultdict


from core.logger import logger



@dataclass(slots=True)
class DocumentMemory:
    """
    Persistent document memory.
    """

    document_id: str


    pages_processed: int = 0


    summary: str = ""


    entities: dict = field(
        default_factory=dict
    )


    extracted_sections: list[str] = field(
        default_factory=list
    )


    important_facts: list[str] = field(
        default_factory=list
    )



class ContextManager:
    """
    External memory manager.

    Prevents small models from
    losing document context.
    """

    def __init__(self):

        self.documents = {}

        logger.info(
            "Context manager initialized"
        )



    def create_memory(
        self,
        document_id: str,
    ) -> DocumentMemory:
        """
        Create document memory.
        """

        memory = DocumentMemory(

            document_id=document_id

        )


        self.documents[document_id] = memory


        return memory



    def update_memory(
        self,
        document_id: str,
        page_number: int,
        extraction: dict,
    ):
        """
        Update memory after each page.
        """


        memory = self.documents[
            document_id
        ]


        memory.pages_processed = (
            page_number
        )


        # Store extracted sections

        if "sections" in extraction:

            memory.extracted_sections.extend(

                extraction["sections"]

            )


        # Store important facts

        if "facts" in extraction:

            memory.important_facts.extend(

                extraction["facts"]

            )


        # Update entities

        if "entities" in extraction:

            for key,value in extraction[
                "entities"
            ].items():

                memory.entities[key] = value



    def build_context(
        self,
        document_id: str,
    ) -> str:
        """
        Build context sent to VLM.
        """


        memory = self.documents[
            document_id
        ]


        context = f"""

DOCUMENT MEMORY

Pages processed:
{memory.pages_processed}


Document summary:

{memory.summary}


Important entities:

{memory.entities}


Important facts:

{memory.important_facts[-20:]}


Previous sections:

{memory.extracted_sections[-10:]}


RULE:

Use this memory only as reference.

Always trust current image first.

Do not invent information.

"""


        return context



    def update_summary(
        self,
        document_id: str,
        summary: str,
    ):
        """
        Update compressed memory.
        """


        memory = self.documents[
            document_id
        ]


        memory.summary = summary



    def clear(
        self,
        document_id: str,
    ):
        """
        Remove memory after completion.
        """

        if document_id in self.documents:

            del self.documents[
                document_id
            ]