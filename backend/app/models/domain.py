"""Core domain models for legal cases and documents."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Case:
    """Represents a legal case."""
    case_id: UUID
    title: str
    year: int
    judge: str
    decision: str
    case_text: str
    court: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Document:
    """Represents an uploaded document."""
    doc_id: UUID
    filename: str
    file_type: str  # .docx, .pdf, .txt
    case_id: Optional[UUID] = None
    uploaded_at: datetime = None
    status: str = "pending"  # pending, processing, indexed, failed


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document."""
    chunk_id: UUID
    doc_id: UUID
    case_id: Optional[UUID]
    text: str
    chunk_index: int
    page_number: Optional[int]
    embedding: Optional[list] = None  # Vector embedding


@dataclass
class SearchResult:
    """Represents a search result."""
    case_id: UUID
    title: str
    year: int
    judge: str
    decision: str
    relevance_score: float
    matched_chunk_id: Optional[UUID] = None
