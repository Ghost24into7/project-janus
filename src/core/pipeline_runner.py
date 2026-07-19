"""
Pipeline execution engine.

Orchestrates the complete OCR Intelligence Engine.

Responsibilities:

- Execute processing stages
- Manage job lifecycle
- Handle checkpoints
- Coordinate resources


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


from pathlib import Path


from core.logger import logger


from core.job_manager import JobManager

from core.checkpoint_manager import CheckpointManager

from core.memory_manager import MemoryManager

from core.model_manager import ModelManager


from models.document import (
    JobStatus,
    PageExtraction,
)


from pipeline.analyzer import PDFAnalyzer

from pipeline.renderer import PDFRenderer

from pipeline.preprocess import ImagePreprocessor

from pipeline.layout import LayoutDetector

from pipeline.extractor import VisionExtractor

from pipeline.assembler import MarkdownAssembler

from pipeline.validator import DocumentValidator



class PipelineRunner:
    """
    Executes complete document pipeline.
    """

    def __init__(self):

        logger.info(
            "Initializing Pipeline Runner"
        )


        self.analyzer = PDFAnalyzer()

        self.renderer = PDFRenderer()

        self.preprocessor = ImagePreprocessor()

        self.layout = LayoutDetector()

        self.extractor = VisionExtractor()

        self.assembler = MarkdownAssembler()

        self.validator = DocumentValidator()


        self.job_manager = JobManager()

        self.memory_manager = MemoryManager()

        self.model_manager = ModelManager()



    def run(
        self,
        pdf_path: Path,
    ):
        """
        Execute document processing.

        Args:
            pdf_path:
                Input PDF path.
        """

        job = (
            self.job_manager.create_job(
                pdf_path.name
            )
        )


        checkpoint = CheckpointManager(
            job.job_id
        )


        try:

            return self._execute(

                pdf_path,

                job.job_id,

                checkpoint,

            )


        except Exception as exc:


            logger.exception(
                "Pipeline failed"
            )


            self.job_manager.fail_job(

                job.job_id,

                str(exc)

            )


            raise



    def _execute(
        self,
        pdf_path: Path,
        job_id: str,
        checkpoint: CheckpointManager,
    ):

        # -----------------------------
        # Model preparation
        # -----------------------------

        self.model_manager.ensure_available()

        self.model_manager.warmup()



        # -----------------------------
        # Analyze
        # -----------------------------

        self.job_manager.update_status(

            job_id,

            JobStatus.ANALYZING,

            10

        )


        metadata = (
            self.analyzer.analyze(
                pdf_path
            )
        )



        # -----------------------------
        # Rendering
        # -----------------------------

        self.job_manager.update_status(

            job_id,

            JobStatus.RENDERING,

            25

        )


        rendered_pages = (
            self.renderer.render_document(

                pdf_path,

                metadata

            )
        )



        extracted_pages = []



        total_pages = len(
            rendered_pages
        )


        # -----------------------------
        # Extraction
        # -----------------------------

        for index, page in enumerate(
            rendered_pages
        ):


            if not self.memory_manager.is_memory_safe():

                self.memory_manager.cleanup()



            self.job_manager.update_status(

                job_id,

                JobStatus.EXTRACTING,

                30 + (
                    index /
                    total_pages
                    *
                    50
                )

            )



            if checkpoint.page_checkpoint_exists(

                page.page_number

            ):

                logger.info(
                    "Skipping page %s from checkpoint",
                    page.page_number
                )

                continue



            processed = (
                self.preprocessor.process(
                    page
                )
            )


            regions = (
                self.layout.detect(
                    processed
                )
            )


            results = []


            for region in regions:

                result = (
                    self.extractor.extract(

                        processed.output_path,

                        region

                    )
                )

                results.append(
                    result
                )



            checkpoint.save_page_result(

                page.page_number,

                results

            )



            extracted_pages.append(

                PageExtraction(

                    page_number=
                    page.page_number,

                    regions=
                    results

                )

            )



        # -----------------------------
        # Assemble
        # -----------------------------

        self.job_manager.update_status(

            job_id,

            JobStatus.ASSEMBLING,

            85

        )


        document = (
            self.assembler.assemble(

                metadata,

                extracted_pages

            )
        )



        # -----------------------------
        # Validate
        # -----------------------------

        self.job_manager.update_status(

            job_id,

            JobStatus.VALIDATING,

            95

        )


        validation = (
            self.validator.validate(
                document
            )
        )


        if not validation.passed:

            logger.warning(
                validation.issues
            )



        self.job_manager.complete_job(
            job_id
        )


        self.model_manager.unload()


        return document