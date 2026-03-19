"""
Upsert functions for each KG entity type.

Each function uses MERGE on the node's id property to ensure idempotency —
running the same data twice does not create duplicates. All nodes receive
a tenant_id for multi-tenant isolation.
"""

import logging
from typing import Any

from graph.neo4j_client import run_query

logger = logging.getLogger(__name__)


async def upsert_client(props: dict[str, Any], tenant_id: str) -> dict[str, Any]:
    """
    Upsert a Client node.

    Required props: id, name.
    Optional: utility_type, hq_state, revenue_band, employee_count, notes.
    """
    cypher = """
        MERGE (n:Client {id: $id})
        SET
            n.tenant_id     = $tenant_id,
            n.name          = $name,
            n.utility_type  = $utility_type,
            n.hq_state      = $hq_state,
            n.revenue_band  = $revenue_band,
            n.employee_count = $employee_count,
            n.notes         = $notes,
            n.updated_at    = datetime()
        ON CREATE SET n.created_at = datetime()
        RETURN n.id AS id
    """
    params = {
        "id": props["id"],
        "tenant_id": tenant_id,
        "name": props["name"],
        "utility_type": props.get("utility_type"),
        "hq_state": props.get("hq_state"),
        "revenue_band": props.get("revenue_band"),
        "employee_count": props.get("employee_count"),
        "notes": props.get("notes"),
    }
    rows = await run_query(cypher, params)
    logger.debug("Upserted Client: %s", props["id"])
    return rows[0] if rows else {}


async def upsert_tech_system(props: dict[str, Any], tenant_id: str) -> dict[str, Any]:
    """
    Upsert a TechSystem node.

    Required props: id, vendor, product_name, category.
    Optional: utility_relevant, description, misconception, common_in_utility_types.
    """
    cypher = """
        MERGE (n:TechSystem {id: $id})
        SET
            n.tenant_id               = $tenant_id,
            n.vendor                  = $vendor,
            n.product_name            = $product_name,
            n.category                = $category,
            n.utility_relevant        = $utility_relevant,
            n.description             = $description,
            n.misconception           = $misconception,
            n.common_in_utility_types = $common_in_utility_types,
            n.updated_at              = datetime()
        ON CREATE SET n.created_at = datetime()
        RETURN n.id AS id
    """
    params = {
        "id": props["id"],
        "tenant_id": tenant_id,
        "vendor": props["vendor"],
        "product_name": props["product_name"],
        "category": props["category"],
        "utility_relevant": props.get("utility_relevant", True),
        "description": props.get("description"),
        "misconception": props.get("misconception"),
        "common_in_utility_types": props.get("common_in_utility_types", []),
    }
    rows = await run_query(cypher, params)
    logger.debug("Upserted TechSystem: %s", props["id"])
    return rows[0] if rows else {}


async def upsert_use_case(props: dict[str, Any], tenant_id: str) -> dict[str, Any]:
    """
    Upsert a UseCase node.

    Required props: id, name, sub_domain.
    Optional: topic, description, priority_score.
    """
    cypher = """
        MERGE (n:UseCase {id: $id})
        SET
            n.tenant_id      = $tenant_id,
            n.name           = $name,
            n.sub_domain     = $sub_domain,
            n.topic          = $topic,
            n.description    = $description,
            n.priority_score = $priority_score,
            n.updated_at     = datetime()
        ON CREATE SET n.created_at = datetime()
        RETURN n.id AS id
    """
    params = {
        "id": props["id"],
        "tenant_id": tenant_id,
        "name": props["name"],
        "sub_domain": props["sub_domain"],
        "topic": props.get("topic"),
        "description": props.get("description"),
        "priority_score": props.get("priority_score", 0.5),
    }
    rows = await run_query(cypher, params)
    logger.debug("Upserted UseCase: %s", props["id"])
    return rows[0] if rows else {}


async def upsert_consultant(props: dict[str, Any], tenant_id: str) -> dict[str, Any]:
    """
    Upsert a Consultant node.

    Required props: id, name.
    Optional: title, utility_experience_years, location, specializations, email.
    """
    cypher = """
        MERGE (n:Consultant {id: $id})
        SET
            n.tenant_id                  = $tenant_id,
            n.name                       = $name,
            n.title                      = $title,
            n.utility_experience_years   = $utility_experience_years,
            n.location                   = $location,
            n.specializations            = $specializations,
            n.email                      = $email,
            n.updated_at                 = datetime()
        ON CREATE SET n.created_at = datetime()
        RETURN n.id AS id
    """
    params = {
        "id": props["id"],
        "tenant_id": tenant_id,
        "name": props["name"],
        "title": props.get("title"),
        "utility_experience_years": props.get("utility_experience_years", 0),
        "location": props.get("location"),
        "specializations": props.get("specializations", []),
        "email": props.get("email"),
    }
    rows = await run_query(cypher, params)
    logger.debug("Upserted Consultant: %s", props["id"])
    return rows[0] if rows else {}


async def upsert_engagement(props: dict[str, Any], tenant_id: str) -> dict[str, Any]:
    """
    Upsert an Engagement node.

    Required props: id, title, client_id.
    Optional: utility_type, start_date, end_date, outcome_summary, phase, status.
    """
    cypher = """
        MERGE (n:Engagement {id: $id})
        SET
            n.tenant_id       = $tenant_id,
            n.title           = $title,
            n.client_id       = $client_id,
            n.utility_type    = $utility_type,
            n.start_date      = $start_date,
            n.end_date        = $end_date,
            n.outcome_summary = $outcome_summary,
            n.phase           = $phase,
            n.status          = $status,
            n.updated_at      = datetime()
        ON CREATE SET n.created_at = datetime()
        RETURN n.id AS id
    """
    params = {
        "id": props["id"],
        "tenant_id": tenant_id,
        "title": props["title"],
        "client_id": props["client_id"],
        "utility_type": props.get("utility_type"),
        "start_date": props.get("start_date"),
        "end_date": props.get("end_date"),
        "outcome_summary": props.get("outcome_summary"),
        "phase": props.get("phase"),
        "status": props.get("status", "completed"),
    }
    rows = await run_query(cypher, params)
    logger.debug("Upserted Engagement: %s", props["id"])
    return rows[0] if rows else {}


async def create_relationship(
    from_id: str,
    from_label: str,
    to_id: str,
    to_label: str,
    rel_type: str,
    props: dict[str, Any],
    tenant_id: str,
) -> bool:
    """
    Create or merge a typed relationship between two existing nodes.

    Uses MERGE to ensure idempotency. Both nodes must already exist.
    Additional relationship properties (e.g. confidence, source_doc_id) can be
    passed via the props dict.

    Args:
        from_id:    ID of the source node.
        from_label: Label of the source node (e.g. "Client").
        to_id:      ID of the target node.
        to_label:   Label of the target node (e.g. "TechSystem").
        rel_type:   Relationship type (e.g. "USES_SYSTEM").
        props:      Additional relationship properties.
        tenant_id:  Tenant isolation filter.

    Returns:
        True if the relationship was created/merged, False on error.
    """
    # Build dynamic SET clause for relationship properties
    set_clauses = ["r.tenant_id = $tenant_id", "r.updated_at = datetime()"]
    for key in props:
        set_clauses.append(f"r.{key} = ${key}")

    set_block = ", ".join(set_clauses)

    cypher = f"""
        MATCH (a:{from_label} {{id: $from_id}})
        MATCH (b:{to_label} {{id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET {set_block}
        RETURN type(r) AS rel_type
    """
    params: dict[str, Any] = {
        "from_id": from_id,
        "to_id": to_id,
        "tenant_id": tenant_id,
        **props,
    }

    try:
        rows = await run_query(cypher, params)
        logger.debug(
            "Relationship %s-[%s]->%s created/merged.", from_id, rel_type, to_id
        )
        return bool(rows)
    except Exception as exc:
        logger.error("Failed to create relationship %s: %s", rel_type, exc)
        return False
