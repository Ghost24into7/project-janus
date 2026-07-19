"""
Application entry point.

Runs the complete OCR Intelligence Engine pipeline.

Author:
    """
    Application entry point.

    Runs the complete OCR Intelligence Engine pipeline.

    Author:
        Myron

    Python:
        3.12+
    """

    from __future__ import annotations


    import sys
    from pathlib import Path

    from core.logger import logger
    from core.pipeline_runner import PipelineRunner


    def main() -> None:
        """
        CLI entry point.
        """

        if len(sys.argv) < 2:
            print("Usage: python main.py <file_path>")
            return

        source_path = Path(sys.argv[1])

        if not source_path.exists():
            print(f"File not found: {source_path}")
            return

        logger.info("Starting pipeline for %s", source_path.name)

        pipeline = PipelineRunner()
        document = pipeline.run(source_path)

        logger.info(
            "Finished pipeline for %s with %s characters",
            source_path.name,
            len(document.markdown),
        )


    if __name__ == "__main__":
        main()