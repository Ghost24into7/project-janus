from core.document_ingestion import DocumentIngestionService


def test_ingest_text_builds_single_page_document():
    service = DocumentIngestionService()

    ingested = service.ingest_text(
        "alpha\nbeta",
        label="legacy_payload",
    )

    assert ingested.metadata.filename == "legacy_payload.txt"
    assert ingested.metadata.total_pages == 1
    assert ingested.metadata.document_type.value == "unknown"
    assert ingested.pages[0].page_number == 1
    assert ingested.pages[0].regions[0].region_id == 1
    assert "alpha" in ingested.pages[0].regions[0].markdown
    assert "beta" in ingested.pages[0].regions[0].markdown
