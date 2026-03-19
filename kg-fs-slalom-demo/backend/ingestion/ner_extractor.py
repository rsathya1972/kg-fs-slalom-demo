"""
Named Entity Recognition extractor using Claude Haiku.

Extracts (subject, predicate, object) triples from document chunks,
with utility-domain entity type hints to improve extraction accuracy.

Phase 1a: Stub implementation — returns empty list.
Phase 1c: Real Claude Haiku call enabled.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Utility-domain entity extraction prompt
_NER_SYSTEM_PROMPT = """You are an expert knowledge graph entity extractor specializing in the
utility industry and Field Service Management (FSM) systems.

Extract structured (subject, predicate, object) triples from the provided text.

Focus on these entity types:
- Client: Electric/gas/water utilities (IOU, municipal, cooperative)
- TechSystem: FSM platforms (SAP PM, Salesforce FSM, IFS, ClickSoftware), GIS (Esri, Smallworld),
  ADMS, SCADA, ERP, OMS, AMI, Mobile apps
- UseCase: FSM use cases — work order management, crew dispatch, mobile field worker, outage response,
  contractor management, asset inspection, GIS integration
- Consultant: Named Slalom consultants with utility experience
- Engagement: Named consulting projects or engagements
- Integration: System-to-system integration patterns

Relationship types to extract:
- USES_SYSTEM (Client → TechSystem)
- HAS_ENGAGEMENT (Client → Engagement)
- LED / PARTICIPATED_IN (Consultant → Engagement)
- RELEVANT_TO (DiscoveryQuestion → UseCase)
- INTEGRATES_WITH (TechSystem → TechSystem)
- ADDRESSES (Engagement → UseCase)

Output format — ONLY a JSON array of triple objects:
[
  {
    "subject": "entity name",
    "subject_type": "EntityLabel",
    "predicate": "RELATIONSHIP_TYPE",
    "object": "entity name",
    "object_type": "EntityLabel",
    "confidence": 0.0 to 1.0,
    "source_excerpt": "brief verbatim excerpt supporting this triple"
  }
]

Rules:
- NEVER fabricate entities not mentioned in the text
- If a system name is ambiguous (e.g., "Oracle"), use surrounding context to disambiguate
- Confidence < 0.50 means you are guessing — include these but mark low confidence
- Return ONLY valid JSON. No markdown fences. No commentary."""

_NER_USER_TEMPLATE = """Extract knowledge graph triples from the following {doc_type} document chunk:

---
{chunk_text}
---

Remember: Return ONLY valid JSON. No markdown fences. No commentary."""


class NERExtractor:
    """
    Named Entity Recognition extractor backed by Claude Haiku.

    Processes document chunks in batch and returns a flat list of
    (subject, predicate, object) triples with confidence scores.
    """

    async def extract(
        self,
        chunks: list[dict[str, Any]],
        doc_type: str,
        tenant_id: str,
    ) -> list[dict[str, Any]]:
        """
        Extract entity triples from a list of document chunks.

        Phase 1a stub — real Claude Haiku call wired in Phase 1c.

        Args:
            chunks:    List of chunk dicts from chunker.chunk_document().
            doc_type:  Document type (narrative, qa_bank, transcript, etc.).
            tenant_id: Tenant identifier for logging.

        Returns:
            List of triple dicts: [{subject, subject_type, predicate, object,
                                    object_type, confidence, source_excerpt}, ...]
        """
        logger.info(
            "NERExtractor.extract called: %d chunks, doc_type=%s, tenant=%s — Phase 1a stub returning []",
            len(chunks),
            doc_type,
            tenant_id,
        )
        # Phase 1a: return empty list
        # Phase 1c: iterate chunks, call Claude Haiku with _NER_SYSTEM_PROMPT / _NER_USER_TEMPLATE,
        #           parse JSON response, flatten into single list, deduplicate by (subject, predicate, object)
        return []
