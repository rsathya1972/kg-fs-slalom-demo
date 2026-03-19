"""Health check endpoint — verifies Neo4j and OpenSearch connectivity."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import settings
from graph.neo4j_client import get_driver

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    neo4j: str
    opensearch: str
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check the health of all downstream services.

    Returns 200 if at least one service is reachable.
    Returns 503 if both Neo4j and OpenSearch are unreachable.
    """
    neo4j_status = "error"
    opensearch_status = "error"

    # Ping Neo4j
    try:
        driver = get_driver()
        async with driver.session(database="neo4j") as session:
            result = await session.run("RETURN 1 AS alive")
            await result.single()
        neo4j_status = "ok"
    except Exception as exc:
        logger.warning("Health check — Neo4j unreachable: %s", exc)

    # Ping OpenSearch
    try:
        from opensearchpy import AsyncOpenSearch

        os_client = AsyncOpenSearch(hosts=[settings.opensearch_endpoint])
        info = await os_client.cluster.health(timeout="5s")
        await os_client.close()
        if info.get("status") in ("green", "yellow"):
            opensearch_status = "ok"
        else:
            opensearch_status = "error"
    except Exception as exc:
        logger.warning("Health check — OpenSearch unreachable: %s", exc)

    both_down = neo4j_status == "error" and opensearch_status == "error"
    overall_status = "degraded" if both_down else "ok"

    response = HealthResponse(
        status=overall_status,
        neo4j=neo4j_status,
        opensearch=opensearch_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    if both_down:
        raise HTTPException(status_code=503, detail=response.model_dump())

    return response
