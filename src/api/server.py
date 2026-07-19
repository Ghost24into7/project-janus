"""
FastAPI application.

Exposes OCR Intelligence Engine
as a service.

Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import shutil

from pathlib import Path


from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
)


from fastapi.responses import (
    FileResponse,
)


from core.logger import logger


from core.pipeline_runner import PipelineRunner

from core.job_manager import JobManager


from models.document import JobStatus


from config.settings import PATHS



# -------------------------------------------------
# Application initialization
# -------------------------------------------------


app = FastAPI(

    title="OCR Intelligence Engine",

    description=
    """
    AI powered document extraction platform
    using local vision models.
    """,

    version="1.0.0"

)



pipeline_runner = PipelineRunner()

job_manager = JobManager()



# -------------------------------------------------
# Health endpoint
# -------------------------------------------------


@app.get("/health")
def health():

    return {

        "status":
        "healthy",

        "service":
        "OCR Intelligence Engine"

    }



# -------------------------------------------------
# Document processing
# -------------------------------------------------


@app.post("/documents/process")
async def process_document(
    file: UploadFile = File(...)
):

    """
    Upload and process PDF.
    """


    if not file.filename.endswith(
        ".pdf"
    ):

        raise HTTPException(

            status_code=400,

            detail=
            "Only PDF files supported"

        )


    input_directory = (
        PATHS.input
    )


    input_directory.mkdir(

        parents=True,

        exist_ok=True

    )


    pdf_path = (

        input_directory

        /

        file.filename

    )


    with pdf_path.open(
        "wb"
    ) as buffer:

        shutil.copyfileobj(

            file.file,

            buffer

        )


    job = job_manager.create_job(

        file.filename

    )


    logger.info(

        "Received document %s",

        file.filename

    )


    # Future:
    #
    # Move to background worker
    #

    pipeline_runner.run(
        pdf_path
    )



    return {

        "job_id":
        job.job_id,

        "status":
        "processing"

    }



# -------------------------------------------------
# Job status
# -------------------------------------------------


@app.get("/jobs/{job_id}")
def get_job_status(
    job_id: str,
):

    try:

        job = (
            job_manager.get_job(
                job_id
            )
        )


        return {

            "job_id":
            job.job_id,


            "status":
            job.status,


            "progress":
            job.progress,


            "error":
            job.error

        }


    except FileNotFoundError:


        raise HTTPException(

            status_code=404,

            detail=
            "Job not found"

        )



# -------------------------------------------------
# Result retrieval
# -------------------------------------------------


@app.get("/jobs/{job_id}/result")
def get_result(
    job_id: str,
):

    result_file = (

        PATHS.output

        /

        "document.md"

    )


    if not result_file.exists():

        raise HTTPException(

            status_code=404,

            detail=
            "Result not ready"

        )


    return FileResponse(

        result_file,

        media_type=
        "text/markdown"

    )