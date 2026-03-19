"""Ingestion API routes — document upload and job tracking."""

import logging
from typing import Any

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestResponse(BaseModel):
    """Response returned when a document ingestion job is queued."""

    job_id: str
    status: str
    message: str


class IngestJobStatus(BaseModel):
    """Status of a single ingestion job."""

    job_id: str
    filename: str
    status: str
    chunk_count: int | None
    entity_count: int | None
    error_message: str | None
    created_at: str
    updated_at: str


@router.post("/document", status_code=202, response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    tenant_id: str = "utilities",
) -> IngestResponse:
    """
    Accept a document upload and queue it for ingestion.

    Supports: PDF, DOCX, TXT, PPTX.
    Processing happens asynchronously — poll /ingest/jobs/{job_id} for status.
    """
    # Phase 1a stub — real pipeline wired up in Phase 1c
    logger.info("Received document upload: %s for tenant: %s", file.filename, tenant_id)
    return IngestResponse(
        job_id="job-placeholder-001",
        status="queued",
        message=f"Document '{file.filename}' queued for ingestion. Phase 1c implementation pending.",
    )


@router.get("/jobs", response_model=list[IngestJobStatus])
async def list_ingest_jobs(tenant_id: str = "utilities") -> list[IngestJobStatus]:
    """
    List all ingestion jobs for a tenant.

    Returns jobs in reverse chronological order.
    """
    # Phase 1a stub
    logger.info("Listing ingest jobs for tenant: %s", tenant_id)
    return []


@router.get("/jobs/{job_id}", response_model=IngestJobStatus)
async def get_ingest_job(job_id: str, tenant_id: str = "utilities") -> IngestJobStatus:
    """
    Get the current status of a specific ingestion job.

    Raises 404 if the job does not exist.
    """
    # Phase 1a stub
    raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found. Phase 1c implementation pending.")
