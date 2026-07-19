"""
Vector database abstraction.

Handles semantic document storage
for RAG pipelines.

Database:
    Qdrant


Responsibilities:

- Create collections
- Store embeddings
- Search documents
- Delete documents


Author:
    Your Name
"""

from __future__ import annotations


from dataclasses import dataclass


from typing import List


from qdrant_client import QdrantClient


from qdrant_client.models import (

    Distance,

    VectorParams,

    PointStruct,

)


from core.logger import logger



@dataclass(slots=True)
class VectorDocument:
    """
    Document chunk representation.
    """

    id: str

    text: str

    embedding: list[float]

    metadata: dict



class VectorStore:
    """
    Qdrant vector database wrapper.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        host: str = "localhost",
        port: int = 6333,
    ):

        self.collection_name = (
            collection_name
        )


        self.client = QdrantClient(

            host=host,

            port=port

        )


        logger.info(
            "Qdrant connected"
        )



    def create_collection(
        self,
        vector_size: int,
    ):
        """
        Create vector collection.
        """


        existing = (

            self.client
            .collection_exists(
                self.collection_name
            )

        )


        if existing:

            return



        self.client.create_collection(

            collection_name=
            self.collection_name,


            vectors_config=
            VectorParams(

                size=vector_size,

                distance=
                Distance.COSINE

            )

        )


        logger.info(
            "Collection created"
        )



    def add_documents(
        self,
        documents: List[VectorDocument],
    ):
        """
        Insert document chunks.
        """

        points = []


        for doc in documents:


            points.append(

                PointStruct(

                    id=doc.id,

                    vector=doc.embedding,

                    payload={

                        "text":
                        doc.text,


                        **doc.metadata

                    }

                )

            )


        self.client.upsert(

            collection_name=
            self.collection_name,


            points=points

        )


        logger.info(

            "%s vectors inserted",

            len(points)

        )



    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ):
        """
        Semantic similarity search.
        """

        results = (

            self.client
            .search(

                collection_name=
                self.collection_name,


                query_vector=
                query_vector,


                limit=limit

            )

        )


        return results



    def delete_document(
        self,
        document_id: str,
    ):
        """
        Remove document vectors.
        """

        self.client.delete(

            collection_name=
            self.collection_name,


            points_selector=[

                document_id

            ]

        )