"""
Core data models for the OCR Intelligence Engine (OIE).

These dataclasses define the contracts between pipeline stages.
Every module exchanges strongly typed objects instead of loosely
structured dictionaries.

Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


# ==========================================================
# ENUMS
# ==========================================================

class DocumentType(Enum):
    """High-level document classification."""

    DIGITAL = "digital"
    SCANNED = "scanned"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class RegionType(Enum):
    """Supported layout region types."""

    TITLE = "title"

    HEADING = "heading"

    PARAGRAPH = "paragraph"

    TABLE = "table"

    IMAGE = "image"

    CAPTION = "caption"

    FOOTER = "footer"

    HEADER = "header"

    PAGE_NUMBER = "page_number"

    LIST = "list"

    CODE = "code"

    EQUATION = "equation"

    UNKNOWN = "unknown"


class OCRStatus(Enum):
    """Processing state."""

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    SKIPPED = "skipped"


# ==========================================================
# BOUNDING BOX
# ==========================================================

@dataclass(slots=True)
class BoundingBox:
    """
    Rectangle in image coordinates.
    """

    x: int

    y: int

    width: int

    height: int


# ==========================================================
# LAYOUT REGION
# ==========================================================

@dataclass(slots=True)
class LayoutRegion:
    """
    Represents a detected document region.
    """

    id: int

    region_type: RegionType

    bbox: BoundingBox

    confidence: float

    page_number: int

    reading_order: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

@dataclass(slots=True)
class ExtractionRequest:
    """
    Input sent to vision model.
    """

    image_path: Path

    region: LayoutRegion

    prompt: str


@dataclass(slots=True)
class ExtractionResponse:
    """
    Vision model response.
    """

    region_id: int

    markdown: str

    confidence: float

    tokens_used: int

    processing_time: float

@dataclass(slots=True)
class PageExtraction:
    """
    Extraction result for one page.
    """

    page_number: int

    regions: list[ExtractionResponse]

@dataclass(slots=True)
class ValidationResult:
    """
    Result of document validation.
    """

    passed: bool

    score: float

    issues: list[str] = field(
        default_factory=list
    )

from enum import Enum


class JobStatus(str, Enum):
    """
    Processing states.
    """

    PENDING = "pending"

    ANALYZING = "analyzing"

    RENDERING = "rendering"

    EXTRACTING = "extracting"

    ASSEMBLING = "assembling"

    VALIDATING = "validating"

    COMPLETED = "completed"

    FAILED = "failed"



@dataclass(slots=True)
class ProcessingJob:
    """
    Represents document processing job.
    """

    job_id: str

    filename: str

    status: JobStatus

    progress: float

    created_at: float

    updated_at: float

    error: str | None = None

# ==========================================================
# PAGE METADATA
# ==========================================================

@dataclass(slots=True)
class PageMetadata:
    """
    Metadata describing a page.
    """

    page_number: int

    width: float

    height: float

    rotation: int

    dpi: int

    scanned: bool

    image_path: Path | None = None

    regions: list[LayoutRegion] = field(default_factory=list)


@dataclass(slots=True)
class RenderedPage:
    """
    Represents a rendered PDF page image.

    This object is passed to preprocessing
    and vision models.
    """

    page_number: int

    image_path: Path

    width: int

    height: int

    dpi: int
@dataclass(slots=True)
class ImageQuality:
    """
    Image quality assessment result.
    """

    width: int

    height: int

    brightness: float

    sharpness: float

    noise_score: float

    quality_score: float

@dataclass(slots=True)
class ProcessedPage:
    """
    Represents an enhanced page image.
    """

    page_number: int

    input_path: Path

    output_path: Path

    quality: ImageQuality

# ==========================================================
# OCR RESULT
# ==========================================================

@dataclass(slots=True)
class OCRResult:
    """
    OCR output from a single layout region.
    """

    page_number: int

    region_id: int

    markdown: str

    confidence: float

    processing_time: float


# ==========================================================
# DOCUMENT METADATA
# ==========================================================

@dataclass(slots=True)
class DocumentMetadata:
    """
    High-level document information.
    """

    filename: str

    total_pages: int

    document_type: DocumentType

    encrypted: bool

    file_size_bytes: int

    recommended_dpi: int

    estimated_runtime_seconds: float

    pages: list[PageMetadata] = field(default_factory=list)


# ==========================================================
# DOCUMENT STATE
# ==========================================================

@dataclass(slots=True)
class DocumentState:
    """
    Maintains cross-page context.
    """

    current_page: int = 0

    current_h1: str = ""

    current_h2: str = ""

    current_h3: str = ""

    open_table: bool = False

    open_list: bool = False

    current_table_columns: list[str] = field(default_factory=list)

    figure_counter: int = 0

    equation_counter: int = 0

    warnings: list[str] = field(default_factory=list)


# ==========================================================
# FINAL DOCUMENT
# ==========================================================

@dataclass(slots=True)
class MarkdownDocument:
    """
    Final reconstructed markdown document.
    """

    metadata: DocumentMetadata

    markdown: str

    processing_time: float

    warnings: list[str] = field(default_factory=list)