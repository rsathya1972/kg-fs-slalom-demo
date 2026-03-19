"""
Ingestion pipeline orchestration for the Slalom Field Services Intelligence Platform.

Document ID derivation:
    document_id = SHA-256(tenant_id + ":" + normalized_filename + ":" + str(file_size_bytes))

This ensures idempotent ingestion — uploading the same file twice for the same tenant
produces the same document_id, allowing the pipeline to detect and skip duplicates.

Pipeline stages (in order):
    1. detect_format  — identify doc type: narrative, qa_bank, transcript, architecture, rfd, industry_ref
    2. chunk          — split into semantically coherent chunks using type-appropriate strategy
    3. extract_entities — run NER via Claude Haiku to produce (subject, predicate, object) triples
    4. resolve_entities — disambiguate extracted terms against existing KG nodes; route low-confidence
                          terms to the human review queue
    5. embed          — generate text embeddings and index chunks into OpenSearch
    6. upsert_kg      — merge resolved entities and relationships into Neo4j
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class IngestPipeline:
    """
    Orchestrates the full document ingestion pipeline.

    Each stage is a discrete async step that updates the IngestionJob status
    and logs structured progress output for observability.
    """

    def __init__(self, tenant_id: str) -> None:
        """
        Initialise the pipeline for a specific tenant.

        Args:
            tenant_id: Tenant identifier for multi-tenant isolation.
        """
        self.tenant_id = tenant_id

    async def process_document(self, job_id: str, file_path: str, tenant_id: str) -> dict:
        """
        Run the full ingestion pipeline for a single document.

        Args:
            job_id:    UUID of the IngestionJob record in SQLite.
            file_path: Absolute path to the uploaded file.
            tenant_id: Tenant identifier (may override instance default for batch operations).

        Returns:
            Summary dict with chunk_count, entity_count, and final status.
        """
        path = Path(file_path)
        filename = path.name

        logger.info(
            '{"event": "pipeline.start", "job_id": "%s", "file": "%s", "tenant": "%s"}',
            job_id,
            filename,
            tenant_id,
        )

        result: dict = {
            "job_id": job_id,
            "filename": filename,
            "chunk_count": 0,
            "entity_count": 0,
            "status": "processing",
        }

        try:
            # Stage 1: detect_format
            content = path.read_text(encoding="utf-8", errors="replace")
            await self._log_stage(job_id, "detect_format", "running")
            from ingestion.chunker import detect_doc_type
            doc_type = detect_doc_type(filename, content)
            await self._log_stage(job_id, "detect_format", "done", {"doc_type": doc_type})

            # Stage 2: chunk
            await self._log_stage(job_id, "chunk", "running")
            from ingestion.chunker import chunk_document
            chunks = chunk_document(content, doc_type)
            result["chunk_count"] = len(chunks)
            await self._log_stage(job_id, "chunk", "done", {"chunk_count": len(chunks)})

            # Stage 3: extract_entities
            await self._log_stage(job_id, "extract_entities", "running")
            from ingestion.ner_extractor import NERExtractor
            extractor = NERExtractor()
            triples = await extractor.extract(chunks, doc_type, tenant_id)
            result["entity_count"] = len(triples)
            await self._log_stage(job_id, "extract_entities", "done", {"triple_count": len(triples)})

            # Stage 4: resolve_entities
            await self._log_stage(job_id, "resolve_entities", "running")
            from ingestion.entity_resolver import EntityResolver
            resolver = EntityResolver()
            resolved = []
            for triple in triples:
                res = await resolver.resolve(triple.get("subject", ""), content[:200], tenant_id)
                resolved.append(res)
            await self._log_stage(job_id, "resolve_entities", "done", {"resolved_count": len(resolved)})

            # Stage 5: embed
            await self._log_stage(job_id, "embed", "running")
            from ingestion.embedder import Embedder
            embedder = Embedder()
            await embedder.embed_chunks(chunks, job_id, tenant_id, {"doc_type": doc_type, "filename": filename})
            await self._log_stage(job_id, "embed", "done")

            # Stage 6: upsert_kg
            await self._log_stage(job_id, "upsert_kg", "running")
            # Phase 1a stub — real upsert wired in Phase 1c when resolved triples have full entity shapes
            await self._log_stage(job_id, "upsert_kg", "done", {"note": "Phase 1c implementation pending"})

            result["status"] = "completed"
            logger.info(
                '{"event": "pipeline.complete", "job_id": "%s", "chunks": %d, "entities": %d}',
                job_id,
                result["chunk_count"],
                result["entity_count"],
            )

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)
            logger.error(
                '{"event": "pipeline.error", "job_id": "%s", "error": "%s"}',
                job_id,
                str(exc),
            )

        return result

    async def _log_stage(
        self,
        job_id: str,
        stage: str,
        status: str,
        extra: dict | None = None,
    ) -> None:
        """
        Emit a structured log line for a pipeline stage transition.

        In Phase 1c this will also update the IngestionJob.status in SQLite.
        """
        payload = {
            "event": f"pipeline.stage.{status}",
            "job_id": job_id,
            "stage": stage,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        if extra:
            payload.update(extra)
        import json
        logger.info(json.dumps(payload))
