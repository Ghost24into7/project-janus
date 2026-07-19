"""
Background document processing worker.

Consumes document jobs and executes
OCR pipeline asynchronously.

Responsibilities:

- Execute pipeline
- Update job state
- Handle failures
- Retry processing


Author:
    Your Name

Python:
    3.12+
"""

from __future__ import annotations


import time

from pathlib import Path


from core.logger import logger

from core.pipeline_runner import PipelineRunner

from core.job_manager import JobManager


from models.document import JobStatus



class DocumentWorker:
    """
    Executes document processing jobs.
    """

    def __init__(self):

        self.pipeline = (
            PipelineRunner()
        )

        self.job_manager = (
            JobManager()
        )


        logger.info(
            "Document worker initialized"
        )



    def process(
        self,
        job_id: str,
        pdf_path: Path,
    ):
        """
        Execute one document job.

        Args:

            job_id:
                Unique job identifier

            pdf_path:
                Input PDF

        """

        try:

            logger.info(
                "Worker started job %s",
                job_id,
            )


            self.job_manager.update_status(

                job_id,

                JobStatus.ANALYZING,

                5

            )


            result = (
                self.pipeline.run(
                    pdf_path
                )
            )


            self.job_manager.complete_job(
                job_id
            )


            logger.info(
                "Job completed %s",
                job_id,
            )


            return result



        except Exception as exc:


            logger.exception(
                "Worker failed job %s",
                job_id,
            )


            self.job_manager.fail_job(

                job_id,

                str(exc)

            )


            raise



    def retry(
        self,
        job_id: str,
        pdf_path: Path,
        retries: int = 3,
    ):
        """
        Retry failed jobs.

        Uses exponential backoff.

        Example:

        Retry 1:
            wait 2 sec

        Retry 2:
            wait 4 sec

        Retry 3:
            wait 8 sec

        """

        attempt = 0


        while attempt < retries:


            try:

                return self.process(

                    job_id,

                    pdf_path

                )


            except Exception:


                attempt += 1


                wait_time = (
                    2 ** attempt
                )


                logger.warning(

                    "Retry %s/%s after %s seconds",

                    attempt,

                    retries,

                    wait_time

                )


                time.sleep(
                    wait_time
                )



        raise RuntimeError(
            "Maximum retries exceeded"
        )