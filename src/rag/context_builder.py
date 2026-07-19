"""
RAG Context Builder.

Creates optimized context
for LLM/VLM consumption.


Responsibilities:

- Merge retrieved chunks
- Remove duplicates
- Limit context size
- Preserve citations
- Optimize prompts


Designed for:

Qwen3-VL 4B


Author:
    Your Name
"""

from __future__ import annotations


import hashlib


from dataclasses import dataclass


from core.logger import logger



@dataclass(slots=True)
class ContextDocument:
    """
    Final context block.
    """

    content: str

    token_estimate: int



class ContextBuilder:
    """
    Builds LLM-ready context.
    """

    def __init__(
        self,

        max_tokens: int = 6000,

    ):

        self.max_tokens = max_tokens


        logger.info(

            "Context builder initialized"

        )



    def _hash_content(
        self,

        text: str,

    ) -> str:
        """
        Create duplicate identifier.
        """

        return hashlib.md5(

            text.encode(
                "utf-8"
            )

        ).hexdigest()



    def remove_duplicates(
        self,

        chunks: list,

    ) -> list:
        """
        Remove repeated chunks.
        """

        seen = set()


        unique = []


        for chunk in chunks:


            key = self._hash_content(

                chunk.text

            )


            if key not in seen:


                unique.append(chunk)

                seen.add(key)



        return unique



    def estimate_tokens(
        self,

        text: str,

    ) -> int:
        """
        Simple token estimation.

        Approximation:

        1 token ≈ 4 characters
        """

        return len(text)//4



    def build(
        self,

        chunks: list,

    ) -> ContextDocument:
        """
        Create final context.
        """


        chunks = self.remove_duplicates(

            chunks

        )


        context = ""

        total_tokens = 0



        for index,chunk in enumerate(

            chunks,

            start=1

        ):


            block = f"""

===== SOURCE {index} =====


Document:

{chunk.metadata.get(
    "document_id",
    "unknown"
)}


Page:

{chunk.metadata.get(
    "page",
    "unknown"
)}


Content:

{chunk.text}


"""


            block_tokens = (

                self.estimate_tokens(
                    block
                )

            )



            if (

                total_tokens

                +

                block_tokens

                >

                self.max_tokens

            ):

                break



            context += block


            total_tokens += block_tokens



        return ContextDocument(

            content=context,

            token_estimate=total_tokens

        )