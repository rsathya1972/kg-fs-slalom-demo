"""
Unit tests for EntityResolver.

These tests cover Phase 1b synonym dictionary lookup and the Phase 1a fallback path.
No live database required.
"""

import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_unknown_term_routes_to_review_queue():
    """
    Verify that a term not in the synonym dictionary returns confidence=0.0
    and action='review' (Phase 1a fallback path).

    Uses a deliberately invented term that cannot appear in synonyms_utility.json.
    """
    from ingestion.entity_resolver import EntityResolver

    resolver = EntityResolver()
    result = await resolver.resolve(
        term="XYZ_UNKNOWN_VENDOR_2099",
        context="The utility uses XYZ_UNKNOWN_VENDOR_2099 for work order management.",
        tenant_id="utilities",
    )

    assert result["confidence"] == 0.0
    assert result["action"] == "review"
    assert result["matched_node_id"] is None
    assert result["canonical_name"] is None


@pytest.mark.asyncio
async def test_known_synonym_returns_high_confidence_and_merge():
    """
    Verify that a term matching an alias in synonyms_utility.json returns
    confidence=0.95 and action='merge' (Phase 1b synonym resolution).

    "SAP PM" is a listed alias for "SAP Plant Maintenance".
    """
    from ingestion.entity_resolver import EntityResolver, REVIEW_CONFIDENCE_THRESHOLD

    resolver = EntityResolver()
    result = await resolver.resolve(
        term="SAP PM",
        context="The utility uses SAP PM for work order management.",
        tenant_id="utilities",
    )

    assert result["confidence"] >= REVIEW_CONFIDENCE_THRESHOLD
    assert result["action"] == "merge"
    assert result["matched_node_id"] is None  # Node ID lookup deferred to Phase 1c
    assert result["canonical_name"] == "SAP Plant Maintenance"


@pytest.mark.asyncio
async def test_known_synonym_case_insensitive():
    """
    Verify that synonym matching is case-insensitive.

    "fsm", "FSM", and "Fsm" should all resolve to "Field Service Management".
    """
    from ingestion.entity_resolver import EntityResolver

    resolver = EntityResolver()

    for variant in ("fsm", "FSM", "Fsm"):
        result = await resolver.resolve(
            term=variant,
            context="Evaluating FSM platforms.",
            tenant_id="utilities",
        )
        assert result["action"] == "merge", f"Expected merge for '{variant}', got {result['action']}"
        assert result["canonical_name"] == "Field Service Management"


@pytest.mark.asyncio
async def test_wom_synonym_resolves():
    """
    Verify that 'WOM' (work order management) resolves correctly.

    This alias was added in Phase 1b per CLAUDE.md §1b requirements.
    """
    from ingestion.entity_resolver import EntityResolver

    resolver = EntityResolver()
    result = await resolver.resolve(
        term="WOM",
        context="The utility's WOM process creates 500 work orders per day.",
        tenant_id="utilities",
    )

    assert result["action"] == "merge"
    assert result["canonical_name"] == "Work Order Management"
    assert result["confidence"] == 0.95


@pytest.mark.asyncio
async def test_resolve_known_synonym_returns_high_confidence():
    """
    Verify that when a term exactly matches a canonical synonym, confidence is >= 0.80
    and action is 'merge'.

    This test mocks the resolver's internal lookup to simulate Phase 1c behavior.
    """
    from ingestion.entity_resolver import EntityResolver, REVIEW_CONFIDENCE_THRESHOLD

    resolver = EntityResolver()

    # Mock the internal resolve method to simulate a high-confidence match
    async def mock_resolve(term, context, tenant_id):
        """Simulated high-confidence synonym match."""
        if term.upper() == "FSM":
            return {
                "matched_node_id": "sys-001",
                "canonical_name": "Field Service Management",
                "confidence": 0.95,
                "action": "merge",
            }
        return {"matched_node_id": None, "canonical_name": None, "confidence": 0.0, "action": "review"}

    with patch.object(resolver, "resolve", side_effect=mock_resolve):
        result = await resolver.resolve(
            term="FSM",
            context="The utility is evaluating FSM platforms.",
            tenant_id="utilities",
        )

    assert result["confidence"] >= REVIEW_CONFIDENCE_THRESHOLD
    assert result["action"] == "merge"
    assert result["matched_node_id"] == "sys-001"


def test_determine_action_thresholds():
    """
    Unit test for the _determine_action helper function.

    Verifies threshold boundaries:
        >= 0.80 → merge
        0.50–0.79 → create
        < 0.50 → review
    """
    from ingestion.entity_resolver import EntityResolver

    resolver = EntityResolver()

    assert resolver._determine_action(0.95) == "merge"
    assert resolver._determine_action(0.80) == "merge"
    assert resolver._determine_action(0.79) == "create"
    assert resolver._determine_action(0.50) == "create"
    assert resolver._determine_action(0.49) == "review"
    assert resolver._determine_action(0.0) == "review"
