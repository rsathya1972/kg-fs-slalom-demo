"""
Batch loader for structured seed data — CSV/JSON files to KG nodes.

Used to bootstrap the knowledge graph with:
    - Technology systems (vendors, categories, utility relevance)
    - Client organizations
    - Consultant profiles
    - Discovery questions with branching logic
    - Integration patterns between systems

All loaders use the upsert functions in graph.upsert for idempotency.
"""

import json
import logging
from pathlib import Path

from graph.upsert import (
    upsert_client,
    upsert_consultant,
    upsert_tech_system,
    upsert_use_case,
    create_relationship,
)

logger = logging.getLogger(__name__)

# Seed data directory relative to project root
_SEED_DIR = Path(__file__).parents[2] / "data" / "seed"
_ONTOLOGY_DIR = Path(__file__).parents[2] / "data" / "ontology"


async def load_tech_systems(json_path: str | Path, tenant_id: str) -> int:
    """
    Load TechSystem seed records from a JSON file and upsert into Neo4j.

    Args:
        json_path:  Path to a JSON file containing a list of TechSystem dicts.
        tenant_id:  Tenant identifier applied to all nodes.

    Returns:
        Number of nodes upserted.
    """
    path = Path(json_path)
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to parse seed file %s: %s", path.name, exc)
        return 0
    count = 0
    for record in records:
        await upsert_tech_system(record, tenant_id)
        count += 1
    logger.info("Loaded %d TechSystem nodes from %s", count, path.name)
    return count


async def load_clients(json_path: str | Path, tenant_id: str) -> int:
    """
    Load Client seed records from a JSON file and upsert into Neo4j.

    Args:
        json_path:  Path to JSON file containing a list of Client dicts.
        tenant_id:  Tenant identifier applied to all nodes.

    Returns:
        Number of nodes upserted.
    """
    path = Path(json_path)
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to parse seed file %s: %s", path.name, exc)
        return 0
    count = 0
    for record in records:
        await upsert_client(record, tenant_id)
        count += 1
    logger.info("Loaded %d Client nodes from %s", count, path.name)
    return count


async def load_consultants(json_path: str | Path, tenant_id: str) -> int:
    """
    Load Consultant seed records from a JSON file and upsert into Neo4j.

    Args:
        json_path:  Path to JSON file containing a list of Consultant dicts.
        tenant_id:  Tenant identifier applied to all nodes.

    Returns:
        Number of nodes upserted.
    """
    path = Path(json_path)
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to parse seed file %s: %s", path.name, exc)
        return 0
    count = 0
    for record in records:
        await upsert_consultant(record, tenant_id)
        count += 1
    logger.info("Loaded %d Consultant nodes from %s", count, path.name)
    return count


async def load_discovery_questions(json_path: str | Path, tenant_id: str) -> int:
    """
    Load DiscoveryQuestion seed records from a JSON file and upsert into Neo4j.

    Each record may include a 'use_case_ids' list to create RELEVANT_TO relationships.

    Args:
        json_path:  Path to JSON file containing a list of DiscoveryQuestion dicts.
        tenant_id:  Tenant identifier applied to all nodes.

    Returns:
        Number of nodes upserted.
    """
    from graph.neo4j_client import run_query

    path = Path(json_path)
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to parse seed file %s: %s", path.name, exc)
        return 0
    count = 0

    for record in records:
        cypher = """
            MERGE (q:DiscoveryQuestion {id: $id})
            SET
                q.tenant_id       = $tenant_id,
                q.text            = $text,
                q.category        = $category,
                q.sequence_order  = $sequence_order,
                q.likely_answers  = $likely_answers,
                q.updated_at      = datetime()
            ON CREATE SET q.created_at = datetime()
        """
        params = {
            "id": record["id"],
            "tenant_id": tenant_id,
            "text": record["text"],
            "category": record.get("category", "technical"),
            "sequence_order": record.get("sequence_order", count),
            "likely_answers": json.dumps(record.get("likely_answers", [])),
        }
        await run_query(cypher, params)

        # Create RELEVANT_TO relationships to UseCases if specified
        for uc_id in record.get("use_case_ids", []):
            await create_relationship(
                from_id=record["id"],
                from_label="DiscoveryQuestion",
                to_id=uc_id,
                to_label="UseCase",
                rel_type="RELEVANT_TO",
                props={"source": "seed_data"},
                tenant_id=tenant_id,
            )

        count += 1

    logger.info("Loaded %d DiscoveryQuestion nodes from %s", count, path.name)
    return count


async def load_integration_patterns(json_path: str | Path, tenant_id: str) -> int:
    """
    Load integration pattern records and create INTEGRATES_WITH relationships in Neo4j.

    Requires TechSystem nodes to already exist (load_tech_systems must run first).

    Args:
        json_path:  Path to JSON file containing a list of integration pattern dicts.
        tenant_id:  Tenant identifier.

    Returns:
        Number of relationships created/merged.
    """
    from graph.neo4j_client import run_query

    path = Path(json_path)
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to parse seed file %s: %s", path.name, exc)
        return 0
    count = 0

    for record in records:
        # Look up system IDs by product name
        from_rows = await run_query(
            "MATCH (s:TechSystem {tenant_id: $t}) WHERE s.product_name = $name RETURN s.id AS id",
            {"t": tenant_id, "name": record["from_system"]},
        )
        to_rows = await run_query(
            "MATCH (s:TechSystem {tenant_id: $t}) WHERE s.product_name = $name RETURN s.id AS id",
            {"t": tenant_id, "name": record["to_system"]},
        )

        if not from_rows or not to_rows:
            logger.warning(
                "Integration pattern %s: could not resolve system '%s' or '%s' — skipping",
                record.get("id"),
                record["from_system"],
                record["to_system"],
            )
            continue

        props = {
            "pattern_description": record.get("pattern_description", ""),
            "integration_type": record.get("integration_type", "unidirectional"),
            "common_middleware": json.dumps(record.get("common_middleware", [])),
            "utility_types": json.dumps(record.get("utility_types", [])),
            "source": "seed_data",
        }

        await create_relationship(
            from_id=from_rows[0]["id"],
            from_label="TechSystem",
            to_id=to_rows[0]["id"],
            to_label="TechSystem",
            rel_type="INTEGRATES_WITH",
            props=props,
            tenant_id=tenant_id,
        )
        count += 1

    logger.info("Loaded %d INTEGRATES_WITH relationships from %s", count, path.name)
    return count


async def run_all_seed_data(tenant_id: str) -> dict[str, int]:
    """
    Load all seed data files into Neo4j in the correct dependency order.

    Order:
        1. tech_systems_utility.json       (no dependencies)
        2. discovery_qa_utility_fsm.json   (no node dependencies, but creates UseCase links)
        3. integration_patterns.json       (requires TechSystem nodes)

    Args:
        tenant_id: Tenant identifier applied to all seed nodes.

    Returns:
        Dict mapping entity type → count of nodes/relationships loaded.
    """
    results: dict[str, int] = {}

    logger.info("Starting seed data load for tenant: %s", tenant_id)

    systems_path = _SEED_DIR / "tech_systems_utility.json"
    if systems_path.exists():
        results["tech_systems"] = await load_tech_systems(systems_path, tenant_id)
    else:
        logger.warning("Seed file not found: %s", systems_path)

    dq_path = _SEED_DIR / "discovery_qa_utility_fsm.json"
    if dq_path.exists():
        results["discovery_questions"] = await load_discovery_questions(dq_path, tenant_id)
    else:
        logger.warning("Seed file not found: %s", dq_path)

    int_path = _SEED_DIR / "integration_patterns.json"
    if int_path.exists():
        results["integration_patterns"] = await load_integration_patterns(int_path, tenant_id)
    else:
        logger.warning("Seed file not found: %s", int_path)

    logger.info("Seed data load complete: %s", results)
    return results
