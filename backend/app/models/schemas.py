"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


# Search
class SearchRequest(BaseModel):
    """Search request."""
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class SearchResultItem(BaseModel):
    """Single search result item."""
    case_id: str
    title: str
    year: int
    judge: str
    decision: str
    relevance_score: float
    matched_chunk_id: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response."""
    results: List[SearchResultItem]
    total: int
    limit: int
    offset: int


# Documents
class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    doc_id: str
    filename: str
    file_type: str
    status: str
    message: str


class DocumentMetadata(BaseModel):
    """Document metadata."""
    doc_id: str
    filename: str
    file_type: str
    uploaded_at: datetime
    status: str


class DocumentListResponse(BaseModel):
    """List of documents."""
    documents: List[DocumentMetadata]
    total: int


# Cases
class CaseDetail(BaseModel):
    """Full case details."""
    case_id: str
    title: str
    year: int
    judge: str
    decision: str
    case_text: str
    court: str
    created_at: datetime
    updated_at: datetime


class CaseListResponse(BaseModel):
    """List of cases with pagination."""
    cases: List[CaseDetail]
    total: int
    limit: int
    offset: int


# Health
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
