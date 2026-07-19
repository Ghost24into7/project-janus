
"""
AI Model Lifecycle Manager.

Controls local vision models.

Backend:
    Ollama

Responsibilities:

- Model availability
- Warmup
- Health monitoring
- Lifecycle control


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import time


import ollama


from dataclasses import dataclass


from config.settings import MODEL


from core.logger import logger



@dataclass(slots=True)
class ModelStatus:
    """
    Current model state.
    """

    name: str

    available: bool

    loaded: bool

    last_check: float



class ModelManager:
    """
    Manages AI model lifecycle.
    """

    def __init__(
        self,
    ) -> None:


        self.model_name = (
            MODEL.model_name
        )


        self.status = (
            None
        )


        logger.info(
            "Model manager initialized for %s",
            self.model_name,
        )



    def check_availability(
        self,
    ) -> bool:
        """
        Check if model exists locally.
        """

        try:

            models = (
                ollama.list()
            )


            available_models = [

                model.model

                for model in models.models

            ]


            exists = (
                self.model_name
                in
                available_models
            )


            self.status = ModelStatus(

                name=self.model_name,

                available=exists,

                loaded=False,

                last_check=time.time(),

            )


            return exists


        except Exception as exc:

            logger.exception(
                "Model availability check failed"
            )

            return False



    def ensure_available(
        self,
    ) -> None:
        """
        Ensure model exists.

        Pulls model if missing.
        """

        if self.check_availability():

            logger.info(
                "Model already available"
            )

            return



        logger.warning(
            "Model missing. Pulling %s",
            self.model_name,
        )


        ollama.pull(
            self.model_name
        )


        logger.info(
            "Model download completed"
        )



    def warmup(
        self,
    ) -> None:
        """
        Load model into memory.

        Prevents first-request delay.
        """

        logger.info(
            "Warming model..."
        )


        try:

            ollama.chat(

                model=self.model_name,

                messages=[

                    {
                        "role":"user",

                        "content":
                        "Hello"

                    }

                ],

                keep_alive="30m",

            )


            if self.status:

                self.status.loaded=True


            logger.info(
                "Model warmup complete"
            )


        except Exception:

            logger.exception(
                "Model warmup failed"
            )


            raise



    def unload(
        self,
    ) -> None:
        """
        Release model memory.
        """

        try:

            ollama.chat(

                model=self.model_name,

                messages=[],

                keep_alive="0",

            )


            logger.info(
                "Model unloaded"
            )


        except Exception:

            logger.exception(
                "Model unload failed"
            )



    def health_check(
        self,
    ) -> ModelStatus:
        """
        Return current state.
        """

        if self.status is None:

            self.check_availability()


        return self.status