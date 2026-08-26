"""Document service for uploading and processing documents."""

import logging
import os
from pathlib import Path
from typing import List, Tuple
from uuid import UUID, uuid4
from datetime import UTC, datetime
from app.config import settings
from app.utils.parsers import parse_document, chunk_text
from app.utils.embeddings import embed_batch
from app.models.domain import Document, DocumentChunk

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document ingestion and processing."""
    
    def __init__(self, document_repo=None, parquet_repo=None):
        """Initialize document service.
        
        Args:
            document_repo: Document repository for storing metadata
            parquet_repo: Parquet repository for storing raw data
        """
        self.document_repo = document_repo
        self.parquet_repo = parquet_repo
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Ensure upload directory exists."""
        Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    
    def process_uploaded_file(self, file_path: str, case_id: UUID = None) -> dict:
        """Process an uploaded document.
        
        Args:
            file_path: Path to uploaded file
            case_id: Optional case ID to associate with document
            
        Returns:
            Processing result with doc_id and status
        """
        try:
            filename = Path(file_path).name
            file_type = Path(file_path).suffix.lower()

            existing_doc_id = None
            if self.document_repo and hasattr(self.document_repo, "get_document_id_by_filename"):
                existing_doc_id = self.document_repo.get_document_id_by_filename(filename)

            doc_id = existing_doc_id or uuid4()
            
            logger.info(f"Processing document: {filename} (ID: {doc_id})")
            if existing_doc_id:
                logger.info(f"Replacing existing indexed document for filename: {filename}")
            
            # Parse document
            text = parse_document(file_path)
            logger.info(f"Extracted {len(text)} characters from {filename}")
            
            # Chunk text with overlap
            chunks = chunk_text(
                text,
                chunk_size=settings.chunk_size,
                overlap=settings.chunk_overlap
            )
            logger.info(f"Created {len(chunks)} chunks from {filename}")
            
            # Generate embeddings for chunks
            embeddings = embed_batch(chunks)
            document = Document(
                doc_id=doc_id,
                filename=filename,
                file_type=file_type.lstrip("."),
                case_id=case_id,
                uploaded_at=datetime.now(UTC),
                status="indexed",
            )
            
            # Store chunks with embeddings
            chunk_objects = []
            for idx, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    chunk_id=uuid4(),
                    doc_id=doc_id,
                    case_id=case_id,
                    text=chunk_content,
                    chunk_index=idx,
                    page_number=None,
                    embedding=embedding
                )
                chunk_objects.append(chunk)
            
            # Store in repositories
            if self.document_repo:
                self.document_repo.initialize_schema()
                self.document_repo.upsert_document(document, text, len(text))
                self.document_repo.store_chunks(chunk_objects)
            
            # Store full text in parquet
            if self.parquet_repo:
                self.parquet_repo.store_document(
                    doc_id=doc_id,
                    filename=filename,
                    file_type=file_type,
                    content=text,
                    case_id=case_id
                )
            
            logger.info(f"Successfully processed document: {filename}")
            
            return {
                "doc_id": str(doc_id),
                "filename": filename,
                "file_type": file_type,
                "status": "indexed",
                "chunks_created": len(chunk_objects),
                "message": f"Document indexed with {len(chunk_objects)} chunks"
            }
        
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise
    
    def delete_document(self, doc_id: UUID) -> bool:
        """Delete a document and its chunks.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Deleting document: {doc_id}")
            if self.document_repo:
                self.document_repo.delete_chunks_by_doc(doc_id)
            if self.parquet_repo:
                self.parquet_repo.delete_document(doc_id)
            logger.info(f"Successfully deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            return False

    def list_documents(self) -> Tuple[List[Document], int]:
        """List indexed documents."""
        if self.document_repo:
            return self.document_repo.list_documents()
        return [], 0
