"""
Context assembler — combines graph facts and vector-retrieved chunks into a
structured context string for the RAG generation prompt.

Output format:
    [GRAPH FACTS]
    <structured knowledge graph facts>

    [RETRIEVED DOCUMENTS]
    [1] Source: <filename> | Type: <doc_type> | Score: <score>
    <chunk text>

    [2] ...

Deduplication: chunks with > 95% character overlap are deduplicated.
Token budget: assembler truncates to max_tokens to stay within Claude's context window.

Phase 1a: Stub — returns empty context string.
Phase 1c: Real assembly enabled.
"""

import difflib
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Deduplication threshold (character-level overlap ratio)
DEDUP_OVERLAP_THRESHOLD = 0.95


def _overlap_ratio(a: str, b: str) -> float:
    """
    Compute the character-level overlap ratio between two strings.

    Uses the shorter string as the reference to measure containment.

    Args:
        a: First string.
        b: Second string.

    Returns:
        Float in [0.0, 1.0] — 1.0 means one string is fully contained in the other.
    """
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def deduplicate_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove chunks that are > DEDUP_OVERLAP_THRESHOLD similar to an already-selected chunk.

    Args:
        chunks: Ranked list of chunk dicts with "text" key.

    Returns:
        Deduplicated list preserving original rank order.
    """
    selected: list[dict[str, Any]] = []
    for chunk in chunks:
        text = chunk.get("text", "")
        is_duplicate = any(
            _overlap_ratio(text, s.get("text", "")) > DEDUP_OVERLAP_THRESHOLD
            for s in selected
        )
        if not is_duplicate:
            selected.append(chunk)
    return selected


class ContextAssembler:
    """
    Assembles a structured prompt context string from graph facts and vector chunks.

    Phase 1a stub — returns empty string.
    Phase 1c will implement full assembly with token budgeting.
    """

    def assemble(
        self,
        graph_facts: list[dict[str, Any]],
        vector_chunks: list[dict[str, Any]],
        max_tokens: int = 6000,
    ) -> str:
        """
        Combine graph facts and retrieved chunks into a single structured context string.

        Phase 1a stub — returns empty string.

        Args:
            graph_facts:   List of fact dicts from graph traversal.
                           Each fact has: subject, predicate, object, confidence.
            vector_chunks: List of ranked chunk dicts from HybridRetriever.
            max_tokens:    Maximum number of tokens for the assembled context.

        Returns:
            Structured context string for inclusion in the RAG generation prompt.
        """
        logger.info(
            "ContextAssembler.assemble: %d graph facts, %d chunks — Phase 1a stub returning ''",
            len(graph_facts),
            len(vector_chunks),
        )

        # Phase 1a: no-op
        # Phase 1c implementation plan:
        #   1. Deduplicate vector_chunks
        #   2. Format graph_facts as structured [GRAPH FACTS] section
        #   3. Format vector_chunks as numbered [RETRIEVED DOCUMENTS] section
        #   4. Measure token count of assembled string (tiktoken)
        #   5. Truncate from the lowest-ranked chunks inward if over budget
        #   6. Return final context string

        return ""
