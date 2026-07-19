"""
Complete RAG Pipeline.

Connects:

Retriever
Reranker
Context Builder


Responsible for:

- End-to-end retrieval workflow
- Context preparation
- Answer generation input


Author:
    Your Name
"""

from __future__ import annotations


from dataclasses import dataclass


from rag.retriever import Retriever

from rag.reranker import Reranker

from rag.context_builder import ContextBuilder


from core.logger import logger



@dataclass(slots=True)
class RAGResponse:
    """
    Final RAG output.
    """

    context: str

    sources: list

    token_count: int



class RAGPipeline:
    """
    Main retrieval intelligence pipeline.
    """

    def __init__(
        self,

        retriever: Retriever,

        reranker: Reranker,

        context_builder: ContextBuilder,

    ):


        self.retriever = retriever


        self.reranker = reranker


        self.context_builder = (
            context_builder
        )


        logger.info(

            "RAG pipeline initialized"

        )



    def prepare_context(
        self,

        question: str,

    ) -> RAGResponse:
        """
        Execute complete retrieval flow.
        """

        logger.info(

            "RAG query started: %s",

            question

        )



        # --------------------------------
        # Step 1:
        # Retrieve candidates
        # --------------------------------

        retrieved_chunks = (

            self.retriever.retrieve(

                question,

                top_k=20

            )

        )



        logger.info(

            "Retrieved %s chunks",

            len(retrieved_chunks)

        )



        # --------------------------------
        # Step 2:
        # Rerank
        # --------------------------------

        ranked_chunks = (

            self.reranker.rerank(

                question,

                retrieved_chunks,

                top_k=5

            )

        )



        logger.info(

            "Reranked chunks: %s",

            len(ranked_chunks)

        )



        # --------------------------------
        # Step 3:
        # Build context
        # --------------------------------

        context_document = (

            self.context_builder.build(

                ranked_chunks

            )

        )



        logger.info(

            "Context prepared"

        )



        return RAGResponse(

            context=
            context_document.content,


            sources=[
                chunk.metadata

                for chunk in ranked_chunks

            ],


            token_count=
            context_document.token_estimate

        )