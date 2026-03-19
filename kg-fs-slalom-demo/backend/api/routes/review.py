"""Review queue API routes — human-in-the-loop entity disambiguation."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/review-queue", tags=["review"])


class ReviewQueueItem(BaseModel):
    """A single item awaiting human review for entity disambiguation."""

    id: str
    tenant_id: str
    term: str
    context_excerpt: str
    candidate_nodes_json: str
    extraction_confidence: float
    disambiguation_status: str
    resolved_node_id: str | None


class ReviewDecision(BaseModel):
    """Human reviewer's decision for a queued item."""

    resolved_node_id: str | None = None
    notes: str | None = None


@router.get("", response_model=list[ReviewQueueItem])
async def get_review_queue(
    tenant_id: str = "utilities",
    status: str = "pending",
) -> list[ReviewQueueItem]:
    """
    List items in the review queue, filtered by disambiguation status.

    Status values: pending | resolved | deferred.
    """
    logger.info("Fetching review queue for tenant: %s, status: %s", tenant_id, status)
    # Phase 1a stub — wired to SQLite in Phase 1c
    return []


@router.post("/{item_id}/approve", response_model=dict)
async def approve_review_item(
    item_id: str,
    decision: ReviewDecision,
    tenant_id: str = "utilities",
) -> dict:
    """
    Approve a review queue item by selecting or confirming the resolved entity node.

    Updates the ReviewQueueItem status to 'resolved' and triggers KG merge.
    """
    logger.info("Approving review item: %s with node: %s", item_id, decision.resolved_node_id)
    raise HTTPException(
        status_code=501,
        detail=f"Review item approval for '{item_id}' not yet implemented. Coming in Phase 1c.",
    )


@router.post("/{item_id}/reject", response_model=dict)
async def reject_review_item(
    item_id: str,
    tenant_id: str = "utilities",
    reason: str = "",
) -> dict:
    """
    Reject a review queue item, marking the extracted entity as unresolvable.

    Sets disambiguation_status to 'deferred'. The term will be skipped in future extractions.
    """
    logger.info("Rejecting review item: %s, reason: %s", item_id, reason)
    raise HTTPException(
        status_code=501,
        detail=f"Review item rejection for '{item_id}' not yet implemented. Coming in Phase 1c.",
    )
