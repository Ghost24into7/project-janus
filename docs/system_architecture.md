# System Architecture Strategy

This repository is a local-first document intelligence platform. The current runtime is optimized around PDF processing, but the long-term system should behave as a governed ingestion and knowledge-building engine that can handle many document and data types on low-end hardware.

## Core principle
Use micro-tasks, not monoliths.

Large documents or large batches should be split into small, resumable units:
- one file at a time,
- one page or record batch at a time,
- one region or chunk at a time,
- one storage write at a time,
- one validation step at a time.

## Canonical pipeline
Every input type should be normalized into the same internal contract:
- source file metadata
- extraction metadata
- canonical text blocks
- structured entities
- provenance and citations
- quality and confidence signals
- governance tags

The internal flow should remain:
1. ingest
2. classify
3. normalize
4. extract
5. chunk
6. validate
7. persist
8. retrieve
9. answer

## Supported input families
The system should treat these as different adapters feeding the same core pipeline:
- PDF and scanned PDF
- DOCX and other office documents
- XLSX and tabular sources
- CSV and TSV
- database exports
- raw database strings or SQL text
- legacy file formats converted through adapters
- mixed bundles and zipped collections

## Low-end device strategy
The 4B model should not be asked to carry the entire system context at once.

Instead:
- keep the model focused on the current micro-task only
- maintain external memory in checkpoints and a structured knowledgebase
- summarize aggressively after each unit of work
- reuse retrieval context instead of re-sending full histories
- prefer small prompts with explicit schema requirements
- prefer deterministic preprocessing before model calls
- avoid parallel work that exceeds RAM or GPU capacity

## Knowledgebase design
A smart knowledgebase should store meaning, not just raw text.

Each stored item should include:
- source identity
- document type
- provenance path
- page/record reference
- normalized content
- extracted entities
- relationships
- timestamps
- confidence and validation state
- retention and sensitivity classification

## Governance
Do not commit or upload sensitive material.

GitHub should only contain:
- source code
- architecture docs
- non-sensitive configs
- safe fixtures and tests

GitHub should not contain:
- `.env` files
- secrets
- credentials
- API keys
- generated data dumps
- large runtime artifacts
- checkpoints or temp outputs

## Practical execution order
To scale this repo safely, the next implementation steps should be:
1. lock down ignore rules and secret hygiene
2. create canonical ingestion interfaces
3. add adapters per file type
4. store extraction output in structured records
5. add retrieval over the structured store
6. add governance and sensitivity filters
7. keep each task resumable and checkpointed

## Current repository reality
Today the codebase is strongest at:
- PDF analysis
- page rendering
- image preprocessing
- heuristic layout detection
- vision extraction
- markdown assembly

It is still missing a unified ingestion layer for non-PDF sources and a formal knowledgebase schema. That should be added in micro-steps rather than one large rewrite.