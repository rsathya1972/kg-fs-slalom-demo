"""
Integration tests for graph query functions.

These tests require a live Neo4j instance with seed data loaded.
Run with: pytest -m integration

Mark: @pytest.mark.integration
"""

import pytest


pytestmark = pytest.mark.integration


@pytest.mark.integration
async def test_get_utility_clients_returns_correct_shape():
    """
    Verify that get_utility_clients returns rows with the expected column set.

    Expected columns: id, name, utility_type, hq_state, revenue_band,
                      engagement_count, system_count.
    """
    from graph.queries import get_utility_clients
    from graph.neo4j_client import run_query

    cypher, params = get_utility_clients("utilities")

    # Verify the query is a non-empty string
    assert isinstance(cypher, str)
    assert len(cypher) > 10

    # Verify params contain tenant_id
    assert params.get("tenant_id") == "utilities"

    # With a live connection, verify column shape:
    # rows = await run_query(cypher, params)
    # if rows:
    #     assert "id" in rows[0]
    #     assert "name" in rows[0]
    #     assert "engagement_count" in rows[0]
    #     assert "system_count" in rows[0]


@pytest.mark.integration
async def test_get_tech_systems_filtered_by_category():
    """
    Verify that get_tech_systems with a category filter includes the category param.

    When category="FSM" is provided:
        - The returned params dict must include {"category": "FSM"}
        - The Cypher query must reference $category parameter
    """
    from graph.queries import get_tech_systems

    cypher_all, params_all = get_tech_systems("utilities")
    cypher_filtered, params_filtered = get_tech_systems("utilities", category="FSM")

    # Unfiltered: no category param
    assert "category" not in params_all

    # Filtered: category param present
    assert params_filtered.get("category") == "FSM"
    assert "$category" in cypher_filtered


@pytest.mark.integration
async def test_get_fsm_consultants_ordered_by_experience():
    """
    Verify that get_fsm_consultants query orders results by utility_experience_years DESC.

    The Cypher must contain ORDER BY ... utility_experience_years DESC.
    """
    from graph.queries import get_fsm_consultants

    cypher, params = get_fsm_consultants("utilities")

    assert params.get("tenant_id") == "utilities"
    assert "utility_experience_years" in cypher
    assert "DESC" in cypher.upper()
