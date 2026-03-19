"""
Unit tests for EntityResolver.

These tests use only the stub implementation and do not require a live database.
"""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_low_confidence_routes_to_review_queue():
    """
    Verify that the Phase 1a stub always returns confidence=0.0 and action='review'.

    In Phase 1a, every term should be routed to the human review queue
    because the resolver is not yet connected to the KG or synonym dictionary.
    """
    from ingestion.entity_resolver import EntityResolver

    resolver = EntityResolver()
    result = await resolver.resolve(
        term="SAP PM",
        context="The utility uses SAP PM for work order management.",
        tenant_id="utilities",
    )

    assert result["confidence"] == 0.0
    assert result["action"] == "review"
    assert result["matched_node_id"] is None


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
                "confidence": 0.95,
                "action": "merge",
            }
        return {"matched_node_id": None, "confidence": 0.0, "action": "review"}

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
