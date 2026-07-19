"""
Job lifecycle manager.

Tracks document processing jobs.

Responsibilities:

- Create jobs
- Update status
- Track progress
- Persist job information


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import json

import time

import uuid


from pathlib import Path


from config.settings import PATHS


from core.logger import logger


from models.document import (
    ProcessingJob,
    JobStatus,
)



class JobManager:
    """
    Controls processing jobs.
    """

    def __init__(self):

        self.storage = (
            PATHS.jobs
        )


        self.storage.mkdir(
            parents=True,
            exist_ok=True,
        )


        logger.info(
            "Job manager initialized"
        )



    def create_job(
        self,
        filename: str,
    ) -> ProcessingJob:
        """
        Create new document job.
        """

        now = time.time()


        job = ProcessingJob(

            job_id=str(
                uuid.uuid4()
            ),

            filename=filename,

            status=JobStatus.PENDING,

            progress=0.0,

            created_at=now,

            updated_at=now,

        )


        self._save(
            job
        )


        logger.info(
            "Created job %s",
            job.job_id,
        )


        return job



    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: float,
    ) -> ProcessingJob:
        """
        Update job progress.
        """

        job = self.get_job(
            job_id
        )


        job.status = status

        job.progress = progress

        job.updated_at = time.time()


        self._save(
            job
        )


        logger.info(
            "Job %s status=%s progress=%s",
            job_id,
            status,
            progress,
        )


        return job



    def fail_job(
        self,
        job_id: str,
        error: str,
    ) -> ProcessingJob:
        """
        Mark job failed.
        """

        job = self.get_job(
            job_id
        )


        job.status = JobStatus.FAILED

        job.error = error

        job.updated_at = time.time()


        self._save(
            job
        )


        return job



    def complete_job(
        self,
        job_id: str,
    ) -> ProcessingJob:
        """
        Mark successful completion.
        """

        return self.update_status(

            job_id,

            JobStatus.COMPLETED,

            100.0,

        )



    def get_job(
        self,
        job_id: str,
    ) -> ProcessingJob:
        """
        Retrieve job.
        """

        path = (
            self.storage
            /
            f"{job_id}.json"
        )


        if not path.exists():

            raise FileNotFoundError(
                f"Job {job_id} not found"
            )


        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )


        return ProcessingJob(
            **data
        )



    def _save(
        self,
        job: ProcessingJob,
    ) -> None:
        """
        Persist job.
        """

        path = (
            self.storage
            /
            f"{job.job_id}.json"
        )


        path.write_text(

            json.dumps(

                {

                    "job_id":job.job_id,

                    "filename":job.filename,

                    "status":job.status.value,

                    "progress":job.progress,

                    "created_at":job.created_at,

                    "updated_at":job.updated_at,

                    "error":job.error,

                },

                indent=4,

            ),

            encoding="utf-8",

        )