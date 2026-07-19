"""
Checkpoint management system.

Stores intermediate pipeline states
to allow recovery after failures.

Responsibilities:

- Save completed pages
- Load previous progress
- Resume interrupted jobs
- Avoid duplicate processing


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import json

from pathlib import Path

from dataclasses import asdict


from config.settings import PATHS

from core.logger import logger


from models.document import (
    ExtractionResponse,
)



class CheckpointManager:
    """
    Manages persistent pipeline state.
    """

    def __init__(
        self,
        document_id: str,
    ) -> None:

        self.directory = (
            PATHS.checkpoints
            /
            document_id
        )


        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )


        logger.info(
            "Checkpoint directory: %s",
            self.directory,
        )



    def page_checkpoint_exists(
        self,
        page_number: int,
    ) -> bool:
        """
        Check whether page is already processed.
        """

        return (
            self._page_file(
                page_number
            )
            .exists()
        )



    def save_page_result(
        self,
        page_number: int,
        results: list[ExtractionResponse],
    ) -> None:
        """
        Save extracted page result.

        Args:
            page_number:
                Current page.

            results:
                Extraction outputs.
        """

        data = {

            "page_number": page_number,

            "regions": [

                asdict(result)

                for result in results

            ]

        }


        checkpoint_file = (
            self._page_file(
                page_number
            )
        )


        checkpoint_file.write_text(
            json.dumps(
                data,
                indent=4,
                default=str,
            ),
            encoding="utf-8",
        )


        logger.info(
            "Saved checkpoint page %s",
            page_number,
        )



    def load_page_result(
        self,
        page_number: int,
    ) -> list[dict]:
        """
        Load existing page result.
        """

        checkpoint_file = (
            self._page_file(
                page_number
            )
        )


        if not checkpoint_file.exists():

            return []


        data = json.loads(
            checkpoint_file.read_text(
                encoding="utf-8"
            )
        )


        return data.get(
            "regions",
            []
        )



    def get_completed_pages(self) -> list[int]:
        """
        Return processed pages.
        """

        completed = []


        for file in self.directory.glob(
            "page_*.json"
        ):

            number = int(
                file.stem.split("_")[1]
            )

            completed.append(
                number
            )


        return sorted(
            completed
        )



    def clear(
        self,
    ) -> None:
        """
        Remove checkpoints.
        """

        for file in self.directory.iterdir():

            file.unlink()


        logger.info(
            "Checkpoint cleared"
        )



    def _page_file(
        self,
        page_number: int,
    ) -> Path:
        """
        Generate checkpoint filename.
        """

        return (
            self.directory
            /
            f"page_{page_number}.json"
        )