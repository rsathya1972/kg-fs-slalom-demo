"""Feedback API routes — thumbs up/down signals for RLHF and retrieval tuning."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    """User feedback on a generated response."""

    response_id: str
    rating: str  # "up" | "down"
    comment: str | None = None
    tenant_id: str = "utilities"
    query_hash: str | None = None


class FeedbackRecord(BaseModel):
    """A stored feedback record."""

    id: str
    tenant_id: str
    query_hash: str | None
    rating: str
    comment: str | None
    response_id: str
    created_at: str


@router.post("", status_code=201, response_model=dict)
async def submit_feedback(request: FeedbackRequest) -> dict:
    """
    Submit thumbs-up or thumbs-down feedback on a generated response.

    Feedback is stored in SQLite and used for retrieval quality monitoring.
    Phase 1c implementation pending.
    """
    logger.info(
        "Feedback received: rating=%s for response=%s", request.rating, request.response_id
    )
    return {
        "status": "accepted",
        "message": "Feedback recorded. Persistent storage wired in Phase 1c.",
    }


@router.get("", response_model=list[FeedbackRecord])
async def list_feedback(tenant_id: str = "utilities") -> list[FeedbackRecord]:
    """
    List all feedback records for a tenant.

    Used for analytics and retrieval quality monitoring.
    """
    logger.info("Listing feedback for tenant: %s", tenant_id)
    # Phase 1a stub
    return []
