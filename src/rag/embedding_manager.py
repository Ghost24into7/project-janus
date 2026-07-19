"""
Embedding Manager.

Creates vector representations
for document chunks.

Model:
    BAAI/bge-m3


Responsibilities:

- Load embedding model
- Generate embeddings
- Batch processing
- Memory optimization
- Cache embeddings


Author:
    Your Name
"""


from __future__ import annotations


import hashlib

import json

from pathlib import Path


from sentence_transformers import SentenceTransformer


from core.logger import logger



class EmbeddingManager:
    """
    Local embedding generation engine.
    """

    def __init__(
        self,
        model_name: str =
        "BAAI/bge-m3",

        cache_dir: str =
        "data/embedding_cache",

    ):


        self.model_name = model_name


        self.cache_dir = Path(
            cache_dir
        )


        self.cache_dir.mkdir(

            parents=True,

            exist_ok=True

        )


        self.model = None


        logger.info(
            "Embedding manager initialized"
        )



    def load_model(
        self,
    ):
        """
        Lazy model loading.

        Model loads only when needed.
        """


        if self.model is None:


            logger.info(

                "Loading embedding model: %s",

                self.model_name

            )


            self.model = SentenceTransformer(

                self.model_name

            )



    def _hash_text(
        self,
        text: str,
    ) -> str:
        """
        Generate cache key.
        """

        return hashlib.sha256(

            text.encode(
                "utf-8"
            )

        ).hexdigest()



    def create_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate single embedding.
        """


        cache_key = self._hash_text(
            text
        )


        cache_file = (

            self.cache_dir

            /

            f"{cache_key}.json"

        )


        # -------------------------
        # Cache lookup
        # -------------------------

        if cache_file.exists():


            return json.loads(

                cache_file.read_text()

            )



        self.load_model()



        vector = self.model.encode(

            text,

            normalize_embeddings=True

        )



        vector = vector.tolist()



        cache_file.write_text(

            json.dumps(vector)

        )


        return vector



    def create_batch_embeddings(
        self,
        texts: list[str],
        batch_size: int = 8,
    ):
        """
        Generate embeddings in batches.

        Important for low RAM systems.
        """


        self.load_model()



        results = []


        for index in range(
            0,
            len(texts),
            batch_size
        ):


            batch = texts[

                index:

                index + batch_size

            ]


            vectors = self.model.encode(

                batch,

                batch_size=batch_size,

                normalize_embeddings=True

            )


            results.extend(

                vectors.tolist()

            )



        return results