"""SQLModel ORM models for the Slalom Field Services Intelligence Platform."""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class IngestionJob(SQLModel, table=True):
    """
    Tracks the lifecycle of a document ingestion pipeline run.

    Status transitions:
        queued → processing → completed | failed → dead_letter (after max retries)
    """

    __tablename__ = "ingestion_job"

    id: str = Field(primary_key=True, description="UUID v4")
    tenant_id: str = Field(index=True)
    document_id: str = Field(description="SHA-256 hash of tenant_id + normalized_filename + file_size")
    filename: str
    file_path: str
    status: str = Field(default="queued", description="queued | processing | completed | failed | dead_letter")
    error_message: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)
    chunk_count: Optional[int] = Field(default=None)
    entity_count: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class ReviewQueueItem(SQLModel, table=True):
    """
    Holds ambiguous extracted entities awaiting human disambiguation review.

    When the NER extractor is uncertain which KG node an extracted term refers to,
    it creates a ReviewQueueItem for human resolution.
    """

    __tablename__ = "review_queue_item"

    id: str = Field(primary_key=True, description="UUID v4")
    tenant_id: str = Field(index=True)
    term: str = Field(description="The ambiguous term extracted from source document")
    context_excerpt: str = Field(description="Surrounding text excerpt for human context")
    candidate_nodes_json: str = Field(description="JSON list of candidate KG node IDs and labels")
    extraction_confidence: float = Field(description="NER extraction confidence 0.0–1.0")
    disambiguation_status: str = Field(
        default="pending",
        description="pending | resolved | deferred",
        index=True,
    )
    resolved_node_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=_now)
    resolved_at: Optional[datetime] = Field(default=None)


class FeedbackRecord(SQLModel, table=True):
    """
    Stores user feedback (thumbs up/down) on generated RAG responses.

    Used for retrieval quality monitoring and future RLHF fine-tuning.
    """

    __tablename__ = "feedback_record"

    id: str = Field(primary_key=True, description="UUID v4")
    tenant_id: str = Field(index=True)
    query_hash: Optional[str] = Field(default=None, description="SHA-256 of the original query text")
    rating: str = Field(description="up | down")
    comment: Optional[str] = Field(default=None)
    response_id: str = Field(description="ID of the generated response being rated")
    created_at: datetime = Field(default_factory=_now)


class AuditLog(SQLModel, table=True):
    """
    Immutable audit log for all significant platform actions.

    Captures ingestion, query, review, and admin operations for compliance.
    """

    __tablename__ = "audit_log"

    id: str = Field(primary_key=True, description="UUID v4")
    tenant_id: str = Field(index=True)
    user_id: Optional[str] = Field(default=None, description="Authenticated user ID, if available")
    action: str = Field(description="e.g. ingest.document.queued, query.submitted, review.approved")
    query_hash: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=_now, index=True)
    metadata_json: Optional[str] = Field(default=None, description="JSON blob of action-specific details")
