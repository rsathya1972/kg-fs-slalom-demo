"""Graph API routes — expose KG entities and named Cypher query execution."""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from graph.neo4j_client import run_query
from graph import queries

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


class CypherQueryRequest(BaseModel):
    """Named Cypher query execution request."""

    query_name: str
    params: dict[str, Any] = {}


class CypherQueryResponse(BaseModel):
    """Response from a named Cypher query execution."""

    query_name: str
    result: list[dict[str, Any]]
    row_count: int


class PaginatedResponse(BaseModel):
    """Standard paginated list response shape."""

    items: list[dict[str, Any]]
    total: int
    limit: int
    offset: int


@router.get("/clients", response_model=PaginatedResponse)
async def get_clients(
    tenant_id: str = "utilities",
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """
    List all utility client nodes with their engagement counts.

    Returns an empty list if no clients are in the graph yet.
    """
    cypher, params = queries.get_utility_clients(tenant_id)
    try:
        rows = await run_query(cypher, params)
        page = rows[offset : offset + limit]
        return PaginatedResponse(items=page, total=len(rows), limit=limit, offset=offset)
    except Exception as exc:
        error_id = str(uuid.uuid4())
        logger.error("Failed to query clients [%s]: %s", error_id, exc)
        raise HTTPException(status_code=500, detail={"detail": "Internal error", "error_id": error_id})


@router.get("/systems", response_model=PaginatedResponse)
async def get_systems(
    tenant_id: str = "utilities",
    category: str | None = Query(default=None, description="Filter by category: FSM, GIS, ADMS, ERP, etc."),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """
    List technology systems, optionally filtered by category.

    Categories: FSM, GIS, ADMS, Asset Mgmt, Mobile, SCADA, ERP, OMS, AMI, Custom.
    """
    cypher, params = queries.get_tech_systems(tenant_id, category)
    try:
        rows = await run_query(cypher, params)
        page = rows[offset : offset + limit]
        return PaginatedResponse(items=page, total=len(rows), limit=limit, offset=offset)
    except Exception as exc:
        error_id = str(uuid.uuid4())
        logger.error("Failed to query systems [%s]: %s", error_id, exc)
        raise HTTPException(status_code=500, detail={"detail": "Internal error", "error_id": error_id})


@router.get("/use-cases", response_model=PaginatedResponse)
async def get_use_cases(
    tenant_id: str = "utilities",
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """
    List all FSM use cases seeded into the graph.

    Returns use cases with their sub-domain and topic classification.
    """
    cypher = """
        MATCH (u:UseCase {tenant_id: $tenant_id})
        RETURN u.id AS id, u.name AS name, u.sub_domain AS sub_domain,
               u.topic AS topic, u.description AS description
        ORDER BY u.sub_domain, u.name
    """
    try:
        rows = await run_query(cypher, {"tenant_id": tenant_id})
        page = rows[offset : offset + limit]
        return PaginatedResponse(items=page, total=len(rows), limit=limit, offset=offset)
    except Exception as exc:
        error_id = str(uuid.uuid4())
        logger.error("Failed to query use cases [%s]: %s", error_id, exc)
        raise HTTPException(status_code=500, detail={"detail": "Internal error", "error_id": error_id})


@router.get("/consultants", response_model=PaginatedResponse)
async def get_consultants(
    tenant_id: str = "utilities",
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """
    List consultants with utility FSM experience, ordered by years of experience.
    """
    cypher, params = queries.get_fsm_consultants(tenant_id)
    try:
        rows = await run_query(cypher, params)
        page = rows[offset : offset + limit]
        return PaginatedResponse(items=page, total=len(rows), limit=limit, offset=offset)
    except Exception as exc:
        error_id = str(uuid.uuid4())
        logger.error("Failed to query consultants [%s]: %s", error_id, exc)
        raise HTTPException(status_code=500, detail={"detail": "Internal error", "error_id": error_id})


@router.post("/query", response_model=CypherQueryResponse)
async def execute_named_query(request: CypherQueryRequest) -> CypherQueryResponse:
    """
    Execute a named Cypher query from the query library.

    Supported query names: get_utility_clients, get_tech_systems,
    get_fsm_consultants, get_client_system_landscape, get_discovery_questions_for_use_case.
    """
    query_map = {
        "get_utility_clients": queries.get_utility_clients,
        "get_tech_systems": queries.get_tech_systems,
        "get_fsm_consultants": queries.get_fsm_consultants,
        "get_client_system_landscape": queries.get_client_system_landscape,
        "get_discovery_questions_for_use_case": queries.get_discovery_questions_for_use_case,
    }

    if request.query_name not in query_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown query name '{request.query_name}'. Available: {list(query_map.keys())}",
        )

    fn = query_map[request.query_name]
    tenant_id = request.params.get("tenant_id", "utilities")

    # Build args depending on query function signature
    if request.query_name == "get_tech_systems":
        cypher, params = fn(tenant_id, request.params.get("category"))
    elif request.query_name in ("get_client_system_landscape", "get_discovery_questions_for_use_case"):
        second_key = "client_name" if request.query_name == "get_client_system_landscape" else "use_case_name"
        second_val = request.params.get(second_key, "")
        cypher, params = fn(tenant_id, second_val)
    else:
        cypher, params = fn(tenant_id)

    try:
        rows = await run_query(cypher, params)
        return CypherQueryResponse(query_name=request.query_name, result=rows, row_count=len(rows))
    except Exception as exc:
        logger.error("Named query '%s' failed: %s", request.query_name, exc)
        raise HTTPException(status_code=500, detail=str(exc))
