"""
Document chunk embedder — indexes chunks into OpenSearch with vector embeddings.

OpenSearch document shape:
    {
        "chunk_id":   "<doc_id>_<chunk_index>",
        "doc_id":     "<sha256_document_id>",
        "tenant_id":  "<tenant>",
        "text":       "<chunk text>",
        "embedding":  [float, ...]  # 3072-dimensional vector (text-embedding-3-large)
        "doc_type":   "<narrative|qa_bank|...>",
        "filename":   "<original filename>",
        "chunk_index": int,
        "metadata":   {...}
    }

Phase 1a: Stub — logs "would embed N chunks" without calling the embedding API.
Phase 1c: Real embedding call via OpenAI text-embedding-3-large or Anthropic Voyage.
"""

import logging
from typing import Any

from config import settings

logger = logging.getLogger(__name__)

# Target embedding dimension for text-embedding-3-large
EMBEDDING_DIMENSION = 3072


class Embedder:
    """
    Embeds document chunks and indexes them into OpenSearch.

    In Phase 1a this is a no-op stub. In Phase 1c the embed_chunks method
    will generate real vectors and bulk-index them.
    """

    def __init__(self) -> None:
        """Initialise the embedder with OpenSearch endpoint from settings."""
        self.index = settings.opensearch_index
        self.endpoint = settings.opensearch_endpoint

    async def embed_chunks(
        self,
        chunks: list[dict[str, Any]],
        doc_id: str,
        tenant_id: str,
        metadata: dict[str, Any],
    ) -> int:
        """
        Generate embeddings for chunks and bulk-index into OpenSearch.

        Phase 1a stub — logs intent without calling the embedding API.

        Args:
            chunks:    List of chunk dicts from chunker.chunk_document().
            doc_id:    SHA-256 document identifier.
            tenant_id: Tenant identifier for index filtering.
            metadata:  Additional metadata (doc_type, filename, etc.) stored per chunk.

        Returns:
            Number of chunks indexed (0 in Phase 1a stub).
        """
        logger.info(
            "Embedder.embed_chunks: would embed %d chunks for doc_id=%s tenant=%s "
            "into index=%s (Phase 1a stub — embedding disabled)",
            len(chunks),
            doc_id,
            tenant_id,
            self.index,
        )

        # Phase 1a: no-op
        # Phase 1c implementation plan:
        #   1. Batch chunks into groups of 100 (API rate limit)
        #   2. Call embedding API: openai.embeddings.create(input=[chunk["text"] for chunk in batch])
        #      OR anthropic voyage embeddings
        #   3. Zip embeddings with chunks to build OS documents
        #   4. opensearch_client.bulk(body=_build_bulk_body(docs))
        #   5. Return total indexed count

        return 0

    def _build_os_document(
        self,
        chunk: dict[str, Any],
        embedding: list[float],
        doc_id: str,
        tenant_id: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build an OpenSearch document from a chunk and its embedding vector.

        Args:
            chunk:     Chunk dict with text, chunk_index, metadata.
            embedding: Float list of length EMBEDDING_DIMENSION.
            doc_id:    SHA-256 document ID.
            tenant_id: Tenant identifier.
            metadata:  Extra metadata (doc_type, filename).

        Returns:
            Dict matching the OpenSearch index mapping.
        """
        return {
            "chunk_id": f"{doc_id}_{chunk['chunk_index']}",
            "doc_id": doc_id,
            "tenant_id": tenant_id,
            "text": chunk["text"],
            "embedding": embedding,
            "doc_type": metadata.get("doc_type", "unknown"),
            "filename": metadata.get("filename", ""),
            "chunk_index": chunk["chunk_index"],
            "metadata": chunk.get("metadata", {}),
        }
