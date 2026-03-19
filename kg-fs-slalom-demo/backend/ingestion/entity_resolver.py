"""
Entity resolution — disambiguates extracted terms against existing KG nodes.

Resolution actions:
    merge:  High confidence (>= 0.80) match to an existing node — update node properties.
    create: Moderate confidence (0.50–0.79) that this is a new entity — create new node.
    review: Low confidence (< 0.50 OR < 0.80 when similar nodes exist) — route to human review queue.

Phase 1b: Synonym dictionary lookup — alias → canonical name with confidence 0.95.
Phase 1c: Real lookup against Neo4j + synonym dictionary, then Claude-assisted disambiguation.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REVIEW_CONFIDENCE_THRESHOLD = 0.80
CREATE_CONFIDENCE_THRESHOLD = 0.50

_SYNONYMS_PATH = Path(__file__).parents[2] / "data" / "ontology" / "synonyms_utility.json"


class EntityResolver:
    """
    Resolves extracted entity terms to existing KG nodes or queues them for human review.

    Phase 1b: Synonym dictionary lookup — alias-matched terms return confidence 0.95
    and action "merge". Unmatched terms still route to the review queue (Phase 1a behaviour).

    Phase 1c will add:
        1. Neo4j node ID lookup for confirmed alias matches
        2. Fuzzy match against existing KG nodes via Levenshtein or embedding similarity
        3. Claude Haiku disambiguation call for near-matches
        4. ReviewQueueItem creation for low-confidence terms
    """

    def __init__(self) -> None:
        """Load and index the synonym dictionary on construction."""
        self._alias_map: dict[str, str] = {}
        self._load_synonyms()

    def _load_synonyms(self) -> None:
        """
        Load synonyms_utility.json and build a lowercase alias → canonical lookup dict.

        Silently skips if the file is missing (unit tests may not have it on path).
        """
        try:
            entries = json.loads(_SYNONYMS_PATH.read_text(encoding="utf-8"))
            for entry in entries:
                canonical = entry["canonical"]
                for alias in entry.get("aliases", []):
                    self._alias_map[alias.lower()] = canonical
            logger.debug(
                "EntityResolver: loaded %d synonym aliases from %s",
                len(self._alias_map),
                _SYNONYMS_PATH.name,
            )
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("EntityResolver: could not load synonym dictionary: %s", exc)

    async def resolve(
        self,
        term: str,
        context: str,
        tenant_id: str,
    ) -> dict[str, Any]:
        """
        Attempt to resolve an extracted entity term to an existing KG node.

        Phase 1b resolution order:
            1. Exact alias match in synonym dictionary → confidence 0.95, action "merge"
            2. No match → confidence 0.0, action "review" (Phase 1a fallback)

        Args:
            term:      The entity name as extracted by NER (e.g. "SAP PM", "Maximo", "SDG&E").
            context:   Surrounding text excerpt for disambiguation context.
            tenant_id: Tenant identifier for KG lookup scope.

        Returns:
            Dict with keys:
                matched_node_id (str | None): ID of matched KG node (None until Phase 1c).
                canonical_name  (str | None): Canonical name from synonym dict, or None.
                confidence (float):           Match confidence 0.0–1.0.
                action (str):                 "merge" | "create" | "review".
        """
        normalized = term.strip().lower()

        # Phase 1b: synonym dictionary lookup
        if normalized in self._alias_map:
            canonical = self._alias_map[normalized]
            logger.info(
                "EntityResolver.resolve: term='%s' → canonical='%s' (alias match, confidence=0.95)",
                term,
                canonical,
            )
            return {
                "matched_node_id": None,  # Neo4j ID lookup deferred to Phase 1c
                "canonical_name": canonical,
                "confidence": 0.95,
                "action": "merge",
            }

        # Phase 1a fallback: route unrecognised terms to human review
        logger.info(
            "EntityResolver.resolve: term='%s' tenant=%s — no alias match, routing to review",
            term,
            tenant_id,
        )
        result: dict[str, Any] = {
            "matched_node_id": None,
            "canonical_name": None,
            "confidence": 0.0,
            "action": "review",
        }

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
