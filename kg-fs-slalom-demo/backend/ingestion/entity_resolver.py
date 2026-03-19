"""
Entity resolution — disambiguates extracted terms against existing KG nodes.

Resolution actions:
    merge:  High confidence (>= 0.80) match to an existing node — update node properties.
    create: Moderate confidence (0.50–0.79) that this is a new entity — create new node.
    review: Low confidence (< 0.50 OR < 0.80 when similar nodes exist) — route to human review queue.

Phase 1a: Stub — always returns confidence 0.0, action "review".
Phase 1c: Real lookup against Neo4j + synonym dictionary, then Claude-assisted disambiguation.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

REVIEW_CONFIDENCE_THRESHOLD = 0.80
CREATE_CONFIDENCE_THRESHOLD = 0.50


class EntityResolver:
    """
    Resolves extracted entity terms to existing KG nodes or queues them for human review.

    Phase 1a stub — every term is routed to the review queue with confidence 0.0.
    Phase 1c will implement:
        1. Exact-match lookup in synonym dictionary (synonyms_utility.json)
        2. Fuzzy match against existing KG nodes via Levenshtein or embedding similarity
        3. Claude Haiku disambiguation call for near-matches
        4. Automatic merge if confidence >= REVIEW_CONFIDENCE_THRESHOLD
        5. ReviewQueueItem creation for low-confidence terms
    """

    async def resolve(
        self,
        term: str,
        context: str,
        tenant_id: str,
    ) -> dict[str, Any]:
        """
        Attempt to resolve an extracted entity term to an existing KG node.

        Args:
            term:      The entity name as extracted by NER (e.g. "SAP PM", "Maximo", "SDG&E").
            context:   Surrounding text excerpt for disambiguation context.
            tenant_id: Tenant identifier for KG lookup scope.

        Returns:
            Dict with keys:
                matched_node_id (str | None): ID of the matched KG node, or None.
                confidence (float):           Match confidence 0.0–1.0.
                action (str):                 "merge" | "create" | "review".
        """
        logger.info(
            "EntityResolver.resolve: term='%s' tenant=%s — Phase 1a stub routing to review",
            term,
            tenant_id,
        )

        # Phase 1a: always route to review
        # Phase 1c: implement full resolution pipeline
        result = {
            "matched_node_id": None,
            "confidence": 0.0,
            "action": "review",
        }

        # If confidence < REVIEW_CONFIDENCE_THRESHOLD → create ReviewQueueItem
        # (Phase 1c will call _create_review_queue_item here)
        if result["confidence"] < REVIEW_CONFIDENCE_THRESHOLD:
            logger.debug(
                "Term '%s' confidence %.2f < %.2f → routing to review queue",
                term,
                result["confidence"],
                REVIEW_CONFIDENCE_THRESHOLD,
            )

        return result

    def _determine_action(self, confidence: float) -> str:
        """
        Map a confidence score to a resolution action.

        Args:
            confidence: Float 0.0–1.0.

        Returns:
            "merge" if >= REVIEW_CONFIDENCE_THRESHOLD,
            "create" if >= CREATE_CONFIDENCE_THRESHOLD,
            "review" otherwise.
        """
        if confidence >= REVIEW_CONFIDENCE_THRESHOLD:
            return "merge"
        if confidence >= CREATE_CONFIDENCE_THRESHOLD:
            return "create"
        return "review"
