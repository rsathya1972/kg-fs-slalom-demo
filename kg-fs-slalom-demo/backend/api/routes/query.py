"""Query API routes — RAG-powered natural language query with SSE streaming."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    """Natural language query request body."""

    question: str
    tenant_id: str = "utilities"
    filters: dict[str, str] = {}
    max_results: int = 5


class QueryResponse(BaseModel):
    """Placeholder query response."""

    id: str
    status: str
    message: str


@router.post("", status_code=202, response_model=QueryResponse)
async def submit_query(request: QueryRequest) -> QueryResponse:
    """
    Submit a natural language query for RAG-powered retrieval and generation.

    Processing is asynchronous — use GET /query/{id}/stream for real-time output.
    Phase 1c implementation pending.
    """
    logger.info("Query received: %s", request.question[:80])
    return QueryResponse(
        id="query-placeholder-001",
        status="accepted",
        message="Query accepted. Hybrid retrieval + generation wired in Phase 1c.",
    )


@router.get("/{query_id}/stream")
async def stream_query_response(query_id: str, tenant_id: str = "utilities"):
    """
    Stream the response for a submitted query via Server-Sent Events.

    Returns text/event-stream. Phase 1c implementation pending.
    """
    raise HTTPException(
        status_code=501,
        detail=f"SSE streaming for query '{query_id}' not yet implemented. Coming in Phase 1c.",
    )
