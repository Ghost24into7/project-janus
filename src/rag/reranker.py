"""
RAG Reranker.

Improves retrieval accuracy by
re-scoring retrieved chunks.

Pipeline:

Retriever
    |
Candidates
    |
Reranker
    |
Final Context


Model:

BAAI/bge-reranker-v2-m3


Author:
    Your Name
"""

from __future__ import annotations


from dataclasses import dataclass


from sentence_transformers import CrossEncoder


from core.logger import logger



@dataclass(slots=True)
class RerankedResult:
    """
    Final ranked document chunk.
    """

    text: str

    score: float

    metadata: dict



class Reranker:
    """
    Cross encoder based reranking.
    """

    def __init__(
        self,
        model_name:
        str =
        "BAAI/bge-reranker-v2-m3",

    ):

        self.model_name = model_name


        self.model = None


        logger.info(
            "Reranker initialized"
        )



    def load_model(self):
        """
        Lazy model loading.
        """

        if self.model is None:


            logger.info(

                "Loading reranker model %s",

                self.model_name

            )


            self.model = CrossEncoder(

                self.model_name

            )



    def rerank(
        self,

        query: str,

        documents: list,

        top_k: int = 5,

    ) -> list[RerankedResult]:
        """
        Rerank retrieved documents.
        """


        if not documents:

            return []



        self.load_model()



        pairs = []


        for doc in documents:


            pairs.append(

                [

                    query,

                    doc.text

                ]

            )



        scores = self.model.predict(

            pairs

        )


        ranked = []


        for doc,score in zip(

            documents,

            scores

        ):


            ranked.append(

                RerankedResult(

                    text=doc.text,

                    score=float(score),

                    metadata=doc.metadata

                )

            )



        ranked.sort(

            key=lambda x:x.score,

            reverse=True

        )


        return ranked[:top_k]