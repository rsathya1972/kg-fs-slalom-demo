"""
Hallucination validator — verifies that named entities in a generated response
appear in the retrieved context, preventing unsupported factual claims.

Strategy:
    For each entity_name in the provided entity list:
        - Check if entity_name (case-insensitive) appears in context_text
        - If the entity appears in response_text but NOT in context_text → flag it

A response passes if all named entities can be grounded in the context.

Note: This is a conservative surface-level check. It does not catch paraphrased
hallucinations or metric fabrication. Claude-based verification is planned for Phase 1c.
"""

import logging
import re

logger = logging.getLogger(__name__)


class HallucinationChecker:
    """
    Post-generation validator that flags entities not grounded in the retrieved context.

    Instantiated once and reused across requests (stateless).
    """

    def check(
        self,
        response_text: str,
        context_text: str,
        entity_names: list[str],
    ) -> dict[str, bool | list[str]]:
        """
        Check whether named entities in the response are grounded in the context.

        Args:
            response_text:  The full generated response text from Claude.
            context_text:   The assembled context string passed to Claude.
            entity_names:   List of entity names to verify (extracted from the query
                            or the KG entity list for this tenant).

        Returns:
            Dict with:
                passed (bool):              True if no ungrounded entities detected.
                flagged_entities (list[str]): Entity names found in response but
                                              not in context. Empty list if passed.
        """
        response_lower = response_text.lower()
        context_lower = context_text.lower()

        flagged: list[str] = []

        for entity in entity_names:
            entity_lower = entity.lower()
            # Use word-boundary regex to avoid substring false positives ("SAP" in "SAPISAPI").
            # Fall back to plain substring check for entities containing special chars (e.g. "SDG&E")
            # where \b anchors don't behave reliably.
            boundary_pattern = r"\b" + re.escape(entity_lower) + r"\b"
            try:
                in_response = bool(re.search(boundary_pattern, response_lower, re.IGNORECASE))
            except re.error:
                in_response = entity_lower in response_lower

            if not in_response:
                continue  # Entity not mentioned — nothing to verify

            try:
                in_context = bool(re.search(boundary_pattern, context_lower, re.IGNORECASE))
            except re.error:
                in_context = entity_lower in context_lower

            if not in_context:
                flagged.append(entity)
                logger.warning(
                    "Hallucination check: entity '%s' appears in response but not in context.",
                    entity,
                )

        passed = len(flagged) == 0
        if passed:
            logger.debug(
                "Hallucination check passed: all %d entities grounded in context.",
                len(entity_names),
            )
        else:
            logger.warning(
                "Hallucination check FAILED: %d ungrounded entities: %s",
                len(flagged),
                flagged,
            )

        return {"passed": passed, "flagged_entities": flagged}
