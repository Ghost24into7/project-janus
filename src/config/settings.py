"""
Global configuration for OCR Intelligence Engine.

All configurable parameters used throughout the application
must live in this module.

Author:
    Myron

Python:
    3.12+

"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ModelConfig:
    """
    Vision model configuration.
    """

    model_name: str = "qwen3-vl:4b"

    host: str = "http://localhost:11434"

    timeout: int = 300


@dataclass(slots=True, frozen=True)
class RenderingConfig:
    """
    PDF rendering configuration.
    """

    minimum_dpi: int = 150

    default_dpi: int = 220

    maximum_dpi: int = 300

    image_format: str = "png"


@dataclass(slots=True, frozen=True)
class ProcessingConfig:
    """
    Runtime behaviour.
    """

    workers: int = 1

    retry_attempts: int = 3

    checkpoint_interval: int = 1

    cache_images: bool = False

    preserve_temp_files: bool = False


@dataclass(slots=True, frozen=True)
class OutputConfig:
    """
    Output configuration.
    """

    markdown_filename: str = "output.md"

    metadata_filename: str = "metadata.json"

    save_page_images: bool = False


@dataclass(slots=True)
class PathConfig:
    """
    Project paths.
    """

    root: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[2]
    )

    def __post_init__(self) -> None:

        self.cache = self.root / "cache"

        self.logs = self.root / "logs"

        self.output = self.root / "output"

        self.temp = self.root / "temp"

        self.prompts = self.root / "prompts"

        self.checkpoints = self.root / "checkpoints"

        self.tests = self.root / "tests"

        self.docs = self.root / "docs"

        for directory in (
            self.cache,
            self.logs,
            self.output,
            self.temp,
            self.prompts,
            self.checkpoints,
            self.tests,
            self.docs,
        ):
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )


MODEL = ModelConfig()

RENDERING = RenderingConfig()

PROCESSING = ProcessingConfig()

OUTPUT = OutputConfig()

PATHS = PathConfig()