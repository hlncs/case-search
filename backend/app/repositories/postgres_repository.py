"""PostgreSQL repositories for documents, chunks, and vector search."""

import logging
import re
from time import perf_counter
from datetime import UTC, datetime
from typing import List, Optional, Tuple
from uuid import UUID

import psycopg2
from psycopg2.extras import execute_values

from app.config import settings
from app.models.domain import Case, Document, DocumentChunk, SearchResult

logger = logging.getLogger(__name__)


def _vector_literal(values: list[float]) -> str:
    """Convert a Python vector to pgvector text literal format."""
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def _year_from_filename(filename: str) -> int:
    """Extract a year from a case filename when present."""
    year_match = re.search(r"\b(19|20)\d{2}\b", filename)
    return int(year_match.group(0)) if year_match else 0


class PostgresDocumentRepository:
    """Repository for storing documents and embeddings in PostgreSQL."""

    def __init__(self, database_url: str = settings.database_url):
        self.database_url = database_url

    def _connect(self):
        return psycopg2.connect(self.database_url)

    def initialize_schema(self) -> None:
        """Create pgvector extension and document tables if needed."""
        start = perf_counter()
        logger.info("PostgreSQL query start: initialize_schema")
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("create extension if not exists vector")
                cur.execute(
                    """
                    create table if not exists documents (
                        doc_id uuid primary key,
                        filename text not null unique,
                        file_type text not null,
                        case_id uuid,
                        uploaded_at timestamptz not null default now(),
                        status text not null default 'indexed',
                        content_length integer not null default 0,
                        full_text text not null default ''
                    )
                    """
                )
                cur.execute(
                    f"""
                    create table if not exists document_chunks (
                        chunk_id uuid primary key,
                        doc_id uuid not null references documents(doc_id) on delete cascade,
                        case_id uuid,
                        text text not null,
                        chunk_index integer not null,
                        page_number integer,
                        embedding vector({settings.embedding_dimension}) not null,
                        created_at timestamptz not null default now(),
                        unique (doc_id, chunk_index)
                    )
                    """
                )
                cur.execute(
                    """
                    create index if not exists document_chunks_doc_id_idx
                    on document_chunks(doc_id)
                    """
                )
                cur.execute(
                    """
                    create index if not exists documents_filename_idx
                    on documents(filename)
                    """
                )
                cur.execute(
                    """
                    create index if not exists document_chunks_embedding_hnsw_idx
                    on document_chunks using hnsw (embedding vector_cosine_ops)
                    """
                )
        logger.info("PostgreSQL query end: initialize_schema (%.3fs)", perf_counter() - start)

    def upsert_document(
        self,
        document: Document,
        content: str,
        content_length: Optional[int] = None,
    ) -> None:
        """Insert or update a document record."""
        start = perf_counter()
        logger.info("PostgreSQL query start: upsert_document doc_id=%s", document.doc_id)
        uploaded_at = document.uploaded_at or datetime.now(UTC)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into documents (
                        doc_id, filename, file_type, case_id,
                        uploaded_at, status, content_length, full_text
                    )
                    values (%s, %s, %s, %s, %s, %s, %s, %s)
                    on conflict (doc_id) do update set
                        filename = excluded.filename,
                        file_type = excluded.file_type,
                        case_id = excluded.case_id,
                        uploaded_at = excluded.uploaded_at,
                        status = excluded.status,
                        content_length = excluded.content_length,
                        full_text = excluded.full_text
                    """,
                    (
                        str(document.doc_id),
                        document.filename,
                        document.file_type,
                        str(document.case_id) if document.case_id else None,
                        uploaded_at,
                        document.status,
                        content_length if content_length is not None else len(content),
                        content,
                    ),
                )
        logger.info("PostgreSQL query end: upsert_document doc_id=%s (%.3fs)", document.doc_id, perf_counter() - start)

    def get_document_id_by_filename(self, filename: str) -> Optional[UUID]:
        """Return document ID for a filename when already indexed."""
        start = perf_counter()
        logger.info("PostgreSQL query start: get_document_id_by_filename filename=%s", filename)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select doc_id
                    from documents
                    where filename = %s
                    """,
                    (filename,),
                )
                row = cur.fetchone()
                result = row[0] if row else None
            logger.info("PostgreSQL query end: get_document_id_by_filename filename=%s found=%s (%.3fs)", filename, bool(result), perf_counter() - start)
            return result

    def store_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Replace chunks for a document with embedded chunks."""
        if not chunks:
            return

        doc_id = chunks[0].doc_id
        start = perf_counter()
        logger.info("PostgreSQL query start: store_chunks doc_id=%s chunks=%d", doc_id, len(chunks))
        rows = [
            (
                str(chunk.chunk_id),
                str(chunk.doc_id),
                str(chunk.case_id) if chunk.case_id else None,
                chunk.text,
                chunk.chunk_index,
                chunk.page_number,
                _vector_literal(chunk.embedding),
            )
            for chunk in chunks
        ]

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("delete from document_chunks where doc_id = %s", (str(doc_id),))
                execute_values(
                    cur,
                    """
                    insert into document_chunks (
                        chunk_id, doc_id, case_id, text,
                        chunk_index, page_number, embedding
                    ) values %s
                    """,
                    rows,
                    template="(%s, %s, %s, %s, %s, %s, %s::vector)",
                )
        logger.info("PostgreSQL query end: store_chunks doc_id=%s chunks=%d (%.3fs)", doc_id, len(chunks), perf_counter() - start)

    def delete_chunks_by_doc(self, doc_id: UUID) -> None:
        """Delete a document and all chunks via cascade."""
        start = perf_counter()
        logger.info("PostgreSQL query start: delete_chunks_by_doc doc_id=%s", doc_id)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("delete from documents where doc_id = %s", (str(doc_id),))
        logger.info("PostgreSQL query end: delete_chunks_by_doc doc_id=%s (%.3fs)", doc_id, perf_counter() - start)

    def list_documents(self) -> Tuple[List[Document], int]:
        """List stored documents."""
        start = perf_counter()
        logger.info("PostgreSQL query start: list_documents")
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("select count(*) from documents")
                total = cur.fetchone()[0]
                cur.execute(
                    """
                    select doc_id, filename, file_type, case_id, uploaded_at, status
                    from documents
                    order by uploaded_at desc, filename
                    """
                )
                documents = [
                    Document(
                        doc_id=row[0],
                        filename=row[1],
                        file_type=row[2],
                        case_id=row[3],
                        uploaded_at=row[4],
                        status=row[5],
                    )
                    for row in cur.fetchall()
                ]
        logger.info("PostgreSQL query end: list_documents total=%d (%.3fs)", total, perf_counter() - start)
        return documents, total

    def get_by_id(self, case_id: UUID) -> Optional[Case]:
        """Return a stored document as a case detail view."""
        start = perf_counter()
        logger.info("PostgreSQL query start: get_by_id case_id=%s", case_id)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select doc_id, filename, uploaded_at, full_text
                    from documents
                    where doc_id = %s
                    """,
                    (str(case_id),),
                )
                row = cur.fetchone()
                if not row:
                    logger.info("PostgreSQL query end: get_by_id case_id=%s found=False (%.3fs)", case_id, perf_counter() - start)
                    return None

                doc_id, filename, uploaded_at, full_text = row
                case = Case(
                    case_id=doc_id,
                    title=filename,
                    year=_year_from_filename(filename),
                    judge="",
                    decision=full_text[:1000],
                    case_text=full_text,
                    court="",
                    created_at=uploaded_at,
                    updated_at=uploaded_at,
                )
        logger.info("PostgreSQL query end: get_by_id case_id=%s found=True (%.3fs)", case_id, perf_counter() - start)
        return case

    def list_all(self, limit: int = 10, offset: int = 0) -> Tuple[List[Case], int]:
        """List stored documents as cases."""
        start = perf_counter()
        logger.info("PostgreSQL query start: list_all limit=%d offset=%d", limit, offset)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("select count(*) from documents")
                total = cur.fetchone()[0]
                cur.execute(
                    """
                    select doc_id, filename, uploaded_at, full_text
                    from documents
                    order by filename
                    limit %s offset %s
                    """,
                    (limit, offset),
                )
                cases = [
                    Case(
                        case_id=row[0],
                        title=row[1],
                        year=_year_from_filename(row[1]),
                        judge="",
                        decision=row[3][:1000],
                        case_text=row[3],
                        court="",
                        created_at=row[2],
                        updated_at=row[2],
                    )
                    for row in cur.fetchall()
                ]
        logger.info("PostgreSQL query end: list_all total=%d returned=%d (%.3fs)", total, len(cases), perf_counter() - start)
        return cases, total

    def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List[SearchResult], int]:
        """Search chunks by cosine distance and return result items."""
        start = perf_counter()
        logger.info(
            "PostgreSQL query start: search_similar embedding_dim=%d limit=%d offset=%d",
            len(query_embedding),
            limit,
            offset,
        )
        query_vector = _vector_literal(query_embedding)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("select count(*) from document_chunks where embedding is not null")
                total = cur.fetchone()[0]
                cur.execute(
                    """
                    select
                        c.chunk_id,
                        c.doc_id,
                        d.filename,
                        c.text,
                        greatest(0, 1 - (c.embedding <=> %s::vector)) as relevance_score
                    from document_chunks c
                    join documents d on d.doc_id = c.doc_id
                    where c.embedding is not null
                    order by c.embedding <=> %s::vector
                    limit %s offset %s
                    """,
                    (query_vector, query_vector, limit, offset),
                )
                results = []
                for chunk_id, doc_id, filename, chunk_text, relevance_score in cur.fetchall():
                    results.append(
                        SearchResult(
                            case_id=doc_id,
                            title=filename,
                            year=_year_from_filename(filename),
                            judge="",
                            decision=chunk_text[:500],
                            relevance_score=float(relevance_score),
                            matched_chunk_id=chunk_id,
                        )
                    )
        logger.info(
            "PostgreSQL query end: search_similar total=%d returned=%d (%.3fs)",
            total,
            len(results),
            perf_counter() - start,
        )
        return results, total