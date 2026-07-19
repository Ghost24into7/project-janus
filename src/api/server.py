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

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config.settings import PATHS
from core.job_manager import JobManager
from core.logger import logger
from core.pipeline_runner import PipelineRunner
from security.safety import DocumentSafetyManager


WEB_DIR = Path(__file__).resolve().parents[1] / "web"


class TextIngestionRequest(BaseModel):
    content: str
    label: str = "legacy_data"


app = FastAPI(
    title="OCR Intelligence Engine",
    description="AI powered document extraction platform using local vision models.",
    version="1.0.0",
)


WEB_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=str(WEB_DIR)),
    name="static",
)

pipeline_runner = PipelineRunner()
job_manager = JobManager()
safety_manager = DocumentSafetyManager()


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "OCR Intelligence Engine",
    }


@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(WEB_DIR / "index.html")


@app.post("/documents/process")
async def process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload and process a supported file."""

    input_directory = PATHS.input
    input_directory.mkdir(parents=True, exist_ok=True)

    safe_name = Path(file.filename).name
    job = job_manager.create_job(safe_name)

    source_path = input_directory / f"{job.job_id}_{safe_name}"

    with source_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    safety_result = safety_manager.validate_file(source_path)

    if not safety_result.allowed:
        job_manager.fail_job(
            job.job_id,
            safety_result.reason or "Upload rejected",
        )

        raise HTTPException(
            status_code=400,
            detail=safety_result.reason or "Upload rejected",
        )

    logger.info("Received document %s", source_path.name)

    background_tasks.add_task(
        pipeline_runner.run,
        source_path,
        job.job_id,
    )

    return {
        "job_id": job.job_id,
        "status": "processing",
        "source": source_path.name,
    }


@app.post("/documents/text")
def process_text(
    payload: TextIngestionRequest,
    background_tasks: BackgroundTasks,
):
    """Process raw text, DB strings, or legacy content."""

    input_directory = PATHS.input
    input_directory.mkdir(parents=True, exist_ok=True)

    safe_label = Path(payload.label).name or "legacy_data"
    job = job_manager.create_job(f"{safe_label}.txt")

    text_path = input_directory / f"{job.job_id}_{safe_label}.txt"
    text_path.write_text(payload.content, encoding="utf-8")

    background_tasks.add_task(
        pipeline_runner.run,
        text_path,
        job.job_id,
    )

    return {
        "job_id": job.job_id,
        "status": "processing",
        "source": text_path.name,
    }


@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    try:
        job = job_manager.get_job(job_id)

        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "progress": job.progress,
            "error": job.error,
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Job not found")


@app.get("/jobs/{job_id}/result")
def get_result(job_id: str):
    result_file = PATHS.output / job_id / "document.md"

    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Result not ready")

    return FileResponse(result_file, media_type="text/markdown")