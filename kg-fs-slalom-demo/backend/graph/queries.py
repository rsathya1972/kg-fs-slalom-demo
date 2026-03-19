"""
Named Cypher query library for the Slalom Field Services Intelligence Platform.

Each function returns a (cypher_string, params_dict) tuple for use with
graph.neo4j_client.run_query(). Queries are parameterized to prevent injection
and always filter by tenant_id for multi-tenant isolation.
"""

from typing import Any


def get_utility_clients(tenant_id: str) -> tuple[str, dict[str, Any]]:
    """
    List utility clients with their engagement count and known system count.

    Returns columns: id, name, utility_type, hq_state, engagement_count, system_count.
    """
    cypher = """
        MATCH (c:Client {tenant_id: $tenant_id})
        OPTIONAL MATCH (c)-[:HAS_ENGAGEMENT]->(e:Engagement)
        OPTIONAL MATCH (c)-[:USES_SYSTEM]->(s:TechSystem)
        RETURN
            c.id            AS id,
            c.name          AS name,
            c.utility_type  AS utility_type,
            c.hq_state      AS hq_state,
            c.revenue_band  AS revenue_band,
            COUNT(DISTINCT e) AS engagement_count,
            COUNT(DISTINCT s) AS system_count
        ORDER BY c.name
    """
    return cypher, {"tenant_id": tenant_id}


def get_tech_systems(
    tenant_id: str, category: str | None = None
) -> tuple[str, dict[str, Any]]:
    """
    List tech systems, optionally filtered by category (FSM, GIS, ADMS, ERP, etc.).

    Returns columns: id, vendor, product_name, category, utility_relevant,
                     description, misconception, client_count.
    """
    if category:
        cypher = """
            MATCH (s:TechSystem {tenant_id: $tenant_id, category: $category})
            OPTIONAL MATCH (c:Client)-[:USES_SYSTEM]->(s)
            RETURN
                s.id            AS id,
                s.vendor        AS vendor,
                s.product_name  AS product_name,
                s.category      AS category,
                s.utility_relevant AS utility_relevant,
                s.description   AS description,
                s.misconception AS misconception,
                COUNT(DISTINCT c) AS client_count
            ORDER BY s.vendor, s.product_name
        """
        params: dict[str, Any] = {"tenant_id": tenant_id, "category": category}
    else:
        cypher = """
            MATCH (s:TechSystem {tenant_id: $tenant_id})
            OPTIONAL MATCH (c:Client)-[:USES_SYSTEM]->(s)
            RETURN
                s.id            AS id,
                s.vendor        AS vendor,
                s.product_name  AS product_name,
                s.category      AS category,
                s.utility_relevant AS utility_relevant,
                s.description   AS description,
                s.misconception AS misconception,
                COUNT(DISTINCT c) AS client_count
            ORDER BY s.category, s.vendor, s.product_name
        """
        params = {"tenant_id": tenant_id}

    return cypher, params


def get_fsm_consultants(tenant_id: str) -> tuple[str, dict[str, Any]]:
    """
    Get consultants with utility FSM experience, ordered by years of experience descending.

    Returns columns: id, name, title, utility_experience_years, engagement_count,
                     fsm_systems (list), specializations (list).
    """
    cypher = """
        MATCH (con:Consultant {tenant_id: $tenant_id})
        WHERE con.utility_experience_years > 0
        OPTIONAL MATCH (con)-[:LED|:PARTICIPATED_IN]->(e:Engagement)
        OPTIONAL MATCH (con)-[:EXPERT_IN]->(s:TechSystem)
        RETURN
            con.id                        AS id,
            con.name                      AS name,
            con.title                     AS title,
            con.utility_experience_years  AS utility_experience_years,
            con.location                  AS location,
            COUNT(DISTINCT e)             AS engagement_count,
            collect(DISTINCT s.product_name) AS fsm_systems,
            con.specializations           AS specializations
        ORDER BY con.utility_experience_years DESC, con.name
    """
    return cypher, {"tenant_id": tenant_id}


def get_client_system_landscape(
    tenant_id: str, client_name: str
) -> tuple[str, dict[str, Any]]:
    """
    Get all technology systems a client uses, with confidence and source document.

    Returns columns: system_id, vendor, product_name, category, confidence, source_doc_id.
    """
    cypher = """
        MATCH (c:Client {tenant_id: $tenant_id, name: $client_name})-[r:USES_SYSTEM]->(s:TechSystem)
        RETURN
            s.id            AS system_id,
            s.vendor        AS vendor,
            s.product_name  AS product_name,
            s.category      AS category,
            r.confidence    AS confidence,
            r.source_doc_id AS source_doc_id
        ORDER BY s.category, s.vendor
    """
    return cypher, {"tenant_id": tenant_id, "client_name": client_name}


def get_clients_by_two_systems(
    tenant_id: str, system1_name: str, system2_name: str
) -> tuple[str, dict[str, Any]]:
    """
    Get utility clients that use both system1 AND system2 simultaneously.

    Useful for queries like "utilities running SAP PM + Esri ArcGIS".

    Returns columns: id, name, utility_type, hq_state, system1, system2.
    """
    cypher = """
        MATCH (c:Client {tenant_id: $tenant_id})-[:USES_SYSTEM]->(s1:TechSystem)
        WHERE s1.product_name CONTAINS $sys1
        MATCH (c)-[:USES_SYSTEM]->(s2:TechSystem)
        WHERE s2.product_name CONTAINS $sys2
        RETURN
            c.id            AS id,
            c.name          AS name,
            c.utility_type  AS utility_type,
            c.hq_state      AS hq_state,
            s1.product_name AS system1,
            s2.product_name AS system2
        ORDER BY c.name
    """
    return cypher, {"tenant_id": tenant_id, "sys1": system1_name, "sys2": system2_name}


def get_systems_by_integration_target(
    tenant_id: str, target_product_name: str
) -> tuple[str, dict[str, Any]]:
    """
    Get TechSystems that INTEGRATES_WITH a given target system (by product_name substring).

    Useful for queries like "what systems integrate with ArcGIS?".

    Returns columns: id, vendor, product_name, category, integration_type,
                     pattern_description.
    """
    cypher = """
        MATCH (source:TechSystem {tenant_id: $tenant_id})-[r:INTEGRATES_WITH]->(target:TechSystem)
        WHERE target.product_name CONTAINS $target_name
        RETURN
            source.id               AS id,
            source.vendor           AS vendor,
            source.product_name     AS product_name,
            source.category         AS category,
            r.integration_type      AS integration_type,
            r.pattern_description   AS pattern_description
        ORDER BY source.category, source.vendor
    """
    return cypher, {"tenant_id": tenant_id, "target_name": target_product_name}


def get_discovery_questions_for_use_case(
    tenant_id: str, use_case_name: str
) -> tuple[str, dict[str, Any]]:
    """
    Get discovery questions relevant to a specific use case, ordered by sequence.

    Returns columns: id, text, category, sequence_order, likely_answers (JSON string).
    """
    cypher = """
        MATCH (q:DiscoveryQuestion {tenant_id: $tenant_id})-[:RELEVANT_TO]->(u:UseCase)
        WHERE u.name CONTAINS $use_case_name
        RETURN
            q.id              AS id,
            q.text            AS text,
            q.category        AS category,
            q.sequence_order  AS sequence_order,
            q.likely_answers  AS likely_answers
        ORDER BY q.sequence_order
    """
    return cypher, {"tenant_id": tenant_id, "use_case_name": use_case_name}
