"""
Observability metrics collector.

Tracks AI pipeline performance,
resource usage and model behavior.


Responsibilities:

- Collect metrics
- Store runtime statistics
- Export reports


Author:
    Your Name

Python:
    3.12+
"""

from __future__ import annotations


import time

import json


from pathlib import Path


from dataclasses import (
    dataclass,
    field,
    asdict,
)


import psutil


from core.logger import logger


from config.settings import PATHS



@dataclass(slots=True)
class PipelineMetrics:
    """
    Runtime metrics for one document.
    """

    document_id: str


    start_time: float


    end_time: float | None = None


    total_pages: int = 0


    completed_pages: int = 0


    failed_pages: int = 0


    retries: int = 0


    model_name: str = ""


    inference_calls: int = 0


    average_latency: float = 0.0


    confidence_scores: list[float] = field(
        default_factory=list
    )


    peak_memory_gb: float = 0.0



class MetricsCollector:
    """
    Collects system and AI metrics.
    """

    def __init__(
        self,
        document_id: str,
    ):

        self.metrics = PipelineMetrics(

            document_id=document_id,

            start_time=time.time(),

        )


        logger.info(
            "Metrics collector started"
        )



    def record_page(
        self,
        success: bool,
    ):
        """
        Track page completion.
        """

        self.metrics.total_pages += 1


        if success:

            self.metrics.completed_pages += 1

        else:

            self.metrics.failed_pages += 1



    def record_inference(
        self,
        latency: float,
        confidence: float | None = None,
    ):
        """
        Track model inference.
        """

        self.metrics.inference_calls += 1


        current_total = (

            self.metrics.average_latency

            *

            (
                self.metrics.inference_calls
                -
                1
            )

        )


        self.metrics.average_latency = (

            current_total

            +

            latency

        ) / self.metrics.inference_calls



        if confidence:

            self.metrics.confidence_scores.append(
                confidence
            )



    def update_memory_usage(
        self,
    ):
        """
        Capture current RAM usage.
        """

        memory = psutil.virtual_memory()


        used_gb = (

            memory.used

            /

            (1024**3)

        )


        self.metrics.peak_memory_gb = max(

            self.metrics.peak_memory_gb,

            used_gb

        )



    def finish(
        self,
    ):
        """
        Complete metrics recording.
        """

        self.metrics.end_time = time.time()


        self.save()



    def save(
        self,
    ):
        """
        Persist metrics.
        """

        directory = (

            PATHS.metrics

        )


        directory.mkdir(

            parents=True,

            exist_ok=True

        )


        file = (

            directory

            /

            f"{self.metrics.document_id}.json"

        )


        file.write_text(

            json.dumps(

                asdict(self.metrics),

                indent=4,

            ),

            encoding="utf-8",

        )


        logger.info(
            "Metrics saved: %s",
            file,
        )