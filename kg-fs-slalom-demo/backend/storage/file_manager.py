"""File storage utilities for uploads and generated outputs."""

import hashlib
import logging
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)


def ensure_dirs() -> None:
    """
    Create UPLOAD_DIR and OUTPUT_DIR if they do not already exist.

    Called once during application startup.
    """
    upload = Path(settings.upload_dir)
    output = Path(settings.output_dir)
    upload.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    logger.info("Storage directories verified: %s, %s", upload, output)


def validate_path(relative_path: str) -> None:
    """
    Raise ValueError if the relative path contains path traversal sequences.

    Prevents directory traversal attacks (e.g., ../../etc/passwd).

    Args:
        relative_path: The relative file path to validate.

    Raises:
        ValueError: If the path contains '..' or an absolute prefix.
    """
    if ".." in relative_path or relative_path.startswith("/"):
        raise ValueError(f"Unsafe path detected: '{relative_path}'")


def get_upload_path(relative_path: str) -> Path:
    """
    Resolve a relative upload path to an absolute Path.

    Args:
        relative_path: Path relative to UPLOAD_DIR (validated for traversal).

    Returns:
        Absolute Path object.

    Raises:
        ValueError: If path traversal is detected.
    """
    validate_path(relative_path)
    return Path(settings.upload_dir).resolve() / relative_path


def generate_document_id(tenant_id: str, filename: str, file_size: int) -> str:
    """
    Generate a stable document ID as SHA-256(tenant_id + normalized_filename + file_size).

    This ensures the same file uploaded twice by the same tenant produces the same ID,
    enabling idempotent ingestion (deduplication at document level).

    Args:
        tenant_id:  Tenant identifier.
        filename:   Original filename (normalized to lowercase, stripped).
        file_size:  File size in bytes.

    Returns:
        Hex-encoded SHA-256 digest string (64 characters).
    """
    normalized = filename.strip().lower()
    content = f"{tenant_id}:{normalized}:{file_size}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def save_upload(file_bytes: bytes, filename: str, tenant_id: str) -> str:
    """
    Save uploaded file bytes to the tenant's upload directory.

    The file is stored at UPLOAD_DIR/{tenant_id}/{filename}.
    If a file with the same path already exists it is overwritten.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename:   Original filename (used as-is; sanitize before calling if needed).
        tenant_id:  Tenant identifier (used as sub-directory).

    Returns:
        Relative path string (e.g. "utilities/myfile.pdf") suitable for storage
        in the database and later retrieval via get_upload_path().
    """
    tenant_dir = Path(settings.upload_dir) / tenant_id
    tenant_dir.mkdir(parents=True, exist_ok=True)

    file_path = tenant_dir / filename
    file_path.write_bytes(file_bytes)

    relative = f"{tenant_id}/{filename}"
    logger.info("Saved upload: %s (%d bytes)", relative, len(file_bytes))
    return relative
