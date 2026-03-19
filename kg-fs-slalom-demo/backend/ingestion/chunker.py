"""
Document type detection and text chunking strategies.

Supported document types:
    - narrative:     Prose documents (project narratives, case studies, SOW sections)
    - qa_bank:       Structured Q&A documents with Q:/A: patterns
    - transcript:    Meeting transcripts with SPEAKER: turn patterns
    - architecture:  Architecture diagrams / technical description docs
    - rfd:           Request for Data / RFP / proposal documents
    - industry_ref:  Industry reference material (whitepapers, standards docs)
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Attempt to use tiktoken for accurate token counting; fall back to word-split estimate
try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")

    def _count_tokens(text: str) -> int:
        """Count tokens using tiktoken cl100k_base encoding."""
        return len(_ENC.encode(text))

    def _split_tokens(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
        """Split text into chunks of max_tokens with overlap_tokens overlap."""
        tokens = _ENC.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunks.append(_ENC.decode(chunk_tokens))
            if end == len(tokens):
                break
            start += max_tokens - overlap_tokens
        return chunks

except ImportError:
    logger.warning("tiktoken not available — using word-split approximation (1 word ≈ 0.75 tokens).")

    def _count_tokens(text: str) -> int:  # type: ignore[misc]
        """Approximate token count using word count."""
        return int(len(text.split()) * 0.75)

    def _split_tokens(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:  # type: ignore[misc]
        """Word-level sliding window approximation."""
        words = text.split()
        approx_words_per_chunk = int(max_tokens / 0.75)
        approx_overlap_words = int(overlap_tokens / 0.75)
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + approx_words_per_chunk, len(words))
            chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start += approx_words_per_chunk - approx_overlap_words
        return chunks


# ---- Document type detection heuristics ----

_QA_PATTERN = re.compile(r"^\s*[Qq]\s*[:\.]\s*", re.MULTILINE)
_TRANSCRIPT_PATTERN = re.compile(r"^\s*[A-Z][A-Z\s]{1,30}:\s*", re.MULTILINE)
_ARCHITECTURE_KEYWORDS = {"diagram", "architecture", "component", "interface", "integration", "api", "endpoint"}
_RFD_KEYWORDS = {"request for", "rfp", "rfd", "requirements", "scope of work", "sow", "deliverable"}


def detect_doc_type(filename: str, content: str) -> str:
    """
    Infer the document type from the filename and a sample of the content.

    Detection priority:
        1. Filename hints (transcript, architecture, rfd)
        2. Content pattern matching (Q:/A: → qa_bank, SPEAKER: → transcript)
        3. Keyword density analysis
        4. Default: narrative

    Args:
        filename: Original upload filename (extension and name are examined).
        content:  Full text content of the document.

    Returns:
        One of: "narrative" | "qa_bank" | "transcript" | "architecture" | "rfd" | "industry_ref"
    """
    name_lower = filename.lower()
    sample = content[:3000].lower()

    # Filename-based hints
    if any(kw in name_lower for kw in ("transcript", "meeting", "interview", "call")):
        return "transcript"
    if any(kw in name_lower for kw in ("architecture", "arch_", "design", "technical")):
        return "architecture"
    if any(kw in name_lower for kw in ("rfp", "rfd", "sow", "proposal", "requirements")):
        return "rfd"
    if any(kw in name_lower for kw in ("qa_", "q_a", "question", "faq", "discovery")):
        return "qa_bank"
    if any(kw in name_lower for kw in ("whitepaper", "reference", "standard", "industry")):
        return "industry_ref"

    # Content pattern matching
    qa_hits = len(_QA_PATTERN.findall(content[:5000]))
    transcript_hits = len(_TRANSCRIPT_PATTERN.findall(content[:5000]))

    if qa_hits >= 3:
        return "qa_bank"
    if transcript_hits >= 4:
        return "transcript"

    # Keyword density
    arch_score = sum(1 for kw in _ARCHITECTURE_KEYWORDS if kw in sample)
    rfd_score = sum(1 for kw in _RFD_KEYWORDS if kw in sample)

    if arch_score >= 3:
        return "architecture"
    if rfd_score >= 2:
        return "rfd"

    return "narrative"


# ---- Chunking strategies ----

def _chunk_narrative(content: str) -> list[dict[str, Any]]:
    """
    512-token sliding window with 10% (≈52 token) overlap.

    Best for: prose project narratives, case study summaries, SOW sections.
    """
    raw_chunks = _split_tokens(content, max_tokens=512, overlap_tokens=52)
    return [
        {"text": chunk, "chunk_index": i, "metadata": {"strategy": "sliding_window_512"}}
        for i, chunk in enumerate(raw_chunks)
        if chunk.strip()
    ]


def _chunk_qa_bank(content: str) -> list[dict[str, Any]]:
    """
    Split on Q:/A: patterns, keeping each Q&A pair as an atomic chunk.

    Best for: discovery question banks, FAQ documents.
    """
    # Match Q:/A: pair blocks
    pattern = re.compile(
        r"(?:^|\n)\s*[Qq]\s*[:\.]\s*(.*?)(?=\n\s*[Qq]\s*[:\.]\s*|\Z)",
        re.DOTALL,
    )
    matches = pattern.findall(content)

    if not matches:
        # Fallback: paragraph-based
        logger.debug("QA pattern not found — falling back to paragraph chunking.")
        return _chunk_paragraphs(content, doc_type="qa_bank")

    chunks = []
    for i, qa_block in enumerate(matches):
        text = qa_block.strip()
        if text:
            chunks.append({
                "text": text,
                "chunk_index": i,
                "metadata": {"strategy": "qa_pair_atomic"},
            })
    return chunks


def _chunk_transcript(content: str) -> list[dict[str, Any]]:
    """
    Split on speaker turn patterns (SPEAKER: or FIRSTNAME LASTNAME:).

    Best for: meeting transcripts, interview recordings.
    """
    # Split on lines that look like "SPEAKER NAME: ..."
    pattern = re.compile(r"(?:^|\n)([A-Z][A-Z\s]{1,30}):\s*", re.MULTILINE)
    parts = pattern.split(content)

    chunks = []
    # parts alternates: [pre_text, speaker, utterance, speaker, utterance, ...]
    i = 1
    chunk_index = 0
    while i < len(parts) - 1:
        speaker = parts[i].strip()
        utterance = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if utterance:
            chunks.append({
                "text": f"{speaker}: {utterance}",
                "chunk_index": chunk_index,
                "metadata": {"strategy": "speaker_turn", "speaker": speaker},
            })
            chunk_index += 1
        i += 2

    if not chunks:
        return _chunk_paragraphs(content, doc_type="transcript")

    return chunks


def _chunk_paragraphs(content: str, doc_type: str = "narrative") -> list[dict[str, Any]]:
    """
    Paragraph-based chunking — split on double newlines.

    Used for: architecture docs, RFDs, industry reference material, and as fallback.
    """
    paragraphs = re.split(r"\n\s*\n", content)
    chunks = []
    for i, para in enumerate(paragraphs):
        text = para.strip()
        if text and _count_tokens(text) > 10:
            chunks.append({
                "text": text,
                "chunk_index": i,
                "metadata": {"strategy": f"paragraph_{doc_type}"},
            })
    return chunks


def chunk_document(content: str, doc_type: str) -> list[dict[str, Any]]:
    """
    Dispatch to the appropriate chunking strategy for a given document type.

    Args:
        content:  Full text of the document.
        doc_type: One of: narrative, qa_bank, transcript, architecture, rfd, industry_ref.

    Returns:
        List of chunk dicts, each containing:
            text (str), chunk_index (int), metadata (dict).
    """
    strategies = {
        "narrative": _chunk_narrative,
        "qa_bank": _chunk_qa_bank,
        "transcript": _chunk_transcript,
        "architecture": lambda c: _chunk_paragraphs(c, "architecture"),
        "rfd": lambda c: _chunk_paragraphs(c, "rfd"),
        "industry_ref": lambda c: _chunk_paragraphs(c, "industry_ref"),
    }

    fn = strategies.get(doc_type, _chunk_narrative)
    chunks = fn(content)
    logger.info("Chunked document: doc_type=%s → %d chunks", doc_type, len(chunks))
    return chunks
