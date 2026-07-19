"""
RAG Retriever.

Finds relevant document chunks
from vector database.


Responsibilities:

- Query embedding
- Similarity search
- Metadata filtering
- Context preparation


Author:
    Your Name
"""

from __future__ import annotations


from dataclasses import dataclass


from rag.vector_store import VectorStore

from rag.embedding_manager import EmbeddingManager


from core.logger import logger



@dataclass(slots=True)
class RetrievalResult:
    """
    Retrieved knowledge chunk.
    """

    text: str

    score: float

    metadata: dict



class Retriever:
    """
    Semantic document retriever.
    """

    def __init__(
        self,
        vector_store: VectorStore,

        embedding_manager:
        EmbeddingManager,

    ):

        self.vector_store = (
            vector_store
        )


        self.embedding_manager = (
            embedding_manager
        )


        logger.info(
            "Retriever initialized"
        )



    def retrieve(
        self,

        query: str,

        top_k: int = 5,

    ) -> list[RetrievalResult]:
        """
        Retrieve relevant chunks.
        """

        # --------------------------
        # Convert query into vector
        # --------------------------

        query_vector = (

            self.embedding_manager

            .create_embedding(
                query
            )

        )


        # --------------------------
        # Search database
        # --------------------------

        results = (

            self.vector_store

            .search(

                query_vector,

                limit=top_k

            )

        )


        retrieved = []


        for item in results:


            retrieved.append(

                RetrievalResult(

                    text=item.payload[

                        "text"

                    ],


                    score=item.score,


                    metadata={

                        key:value

                        for key,value

                        in item.payload.items()

                        if key != "text"

                    }

                )

            )


        return retrieved



    def build_context(
        self,

        results:
        list[RetrievalResult],

    ) -> str:
        """
        Create LLM context.
        """

        context = ""


        for index,result in enumerate(
            results,
            start=1
        ):


            context += f"""

SOURCE {index}

Relevance:
{result.score}


Content:

{result.text}


Metadata:

{result.metadata}

---------------------

"""


        return context