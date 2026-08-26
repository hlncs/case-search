#!/usr/bin/env python3
"""
Initialize documents from the cases folder.

This script processes all documents in the cases/ folder and stores them
in the database with embeddings and chunks.

Usage:
    source venv/bin/activate
    python scripts/init_documents.py
"""

import os
import sys
from pathlib import Path
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid5

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.utils.parsers import parse_document, chunk_text
from app.utils.embeddings import embed_batch
from app.models.domain import Document, DocumentChunk
from app.repositories.postgres_repository import PostgresDocumentRepository
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_valid_documents(cases_dir: str) -> list[Path]:
    """Get all .docx files from cases directory, excluding Windows ADS files."""
    cases_path = Path(cases_dir)
    if not cases_path.exists():
        logger.error(f"Cases directory not found: {cases_dir}")
        return []
    
    # Get only .docx files, excluding Windows alternate data streams
    docx_files = [
        f for f in cases_path.glob("*.docx")
        if f.suffix == ".docx" and "Zone.Identifier" not in f.name and "sec.endpointdlp" not in f.name
    ]
    
    logger.info(f"Found {len(docx_files)} .docx files in {cases_dir}")
    return sorted(docx_files)


def process_document_file(file_path: Path) -> dict:
    """Process a single document file."""
    logger.info(f"Processing: {file_path.name}")
    
    try:
        # Parse document
        text_content = parse_document(str(file_path))
        if not text_content:
            logger.warning(f"  No content extracted from {file_path.name}")
            return {"status": "failed", "reason": "No content extracted"}
        
        # Chunk text
        chunks = chunk_text(
            text_content,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap
        )
        
        # Create document ID from filename
        doc_id = file_path.stem.replace(" ", "_").replace("[", "").replace("]", "").lower()
        
        logger.info(f"  ✓ Extracted {len(chunks)} chunks from {file_path.name}")
        logger.info(f"  Content size: {len(text_content)} characters")
        
        return {
            "status": "success",
            "doc_id": str(uuid5(NAMESPACE_URL, f"case-search:{file_path.name}")),
            "slug": doc_id,
            "filename": file_path.name,
            "file_type": "docx",
            "chunks": len(chunks),
            "content_length": len(text_content),
            "content": text_content,
            "chunks_text": chunks,
        }
    
    except Exception as e:
        logger.error(f"  ✗ Error processing {file_path.name}: {str(e)}")
        return {"status": "failed", "reason": str(e)}


def save_to_postgres(document_repo: PostgresDocumentRepository, result: dict) -> None:
    """Generate embeddings and save a processed document to PostgreSQL."""
    doc_id = uuid5(NAMESPACE_URL, f"case-search:{result['filename']}")
    document = Document(
        doc_id=doc_id,
        filename=result["filename"],
        file_type=result["file_type"],
        uploaded_at=datetime.now(UTC),
        status="indexed",
    )

    logger.info(f"  Generating embeddings for {result['chunks']} chunks")
    embeddings = embed_batch(result["chunks_text"])
    chunk_objects = [
        DocumentChunk(
            chunk_id=uuid5(NAMESPACE_URL, f"case-search:{result['filename']}:chunk:{index}"),
            doc_id=doc_id,
            case_id=None,
            text=chunk_text_value,
            chunk_index=index,
            page_number=None,
            embedding=embedding,
        )
        for index, (chunk_text_value, embedding) in enumerate(zip(result["chunks_text"], embeddings))
    ]

    document_repo.upsert_document(document, result["content"], result["content_length"])
    document_repo.store_chunks(chunk_objects)
    logger.info(f"  Saved {len(chunk_objects)} embedded chunks to PostgreSQL")


def main():
    """Main initialization function."""
    logger.info("=" * 70)
    logger.info("LEGAL CASE SEARCH - Document Initialization")
    logger.info("=" * 70)
    
    # Get the project root (parent of backend directory)
    project_root = Path(__file__).parent.parent.parent
    cases_dir = project_root / "cases"
    
    # Get valid documents
    doc_files = get_valid_documents(str(cases_dir))
    if not doc_files:
        logger.error("No .docx files found to process")
        return
    
    document_repo = PostgresDocumentRepository()
    document_repo.initialize_schema()
    
    logger.info(f"\n{'Processing Documents':^70}")
    logger.info("-" * 70)
    
    results = {
        "total": len(doc_files),
        "successful": 0,
        "failed": 0,
        "documents": [],
    }
    
    # Process each document
    for doc_file in doc_files:
        result = process_document_file(doc_file)
        
        if result["status"] == "success":
            results["successful"] += 1
            results["documents"].append(result)
            save_to_postgres(document_repo, result)
        else:
            results["failed"] += 1
            logger.error(f"Failed to process {doc_file.name}: {result.get('reason', 'Unknown error')}")
    
    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("INITIALIZATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total files processed: {results['total']}")
    logger.info(f"Successful: {results['successful']} ✓")
    logger.info(f"Failed: {results['failed']} ✗")
    
    if results["successful"] > 0:
        logger.info("\nProcessed documents:")
        for doc in results["documents"]:
            logger.info(f"  • {doc['filename']}")
            logger.info(f"    ID: {doc['doc_id']}")
            logger.info(f"    Chunks: {doc['chunks']}")
            logger.info(f"    Content: {doc['content_length']} chars")
    
    logger.info("\n" + "=" * 70)
    logger.info("Next steps:")
    logger.info("1. Start the backend: python -m uvicorn app.main:app --reload")
    logger.info("2. Visit http://localhost:8000/docs for API documentation")
    logger.info("3. Use the /api/search endpoint to search documents")
    logger.info("=" * 70 + "\n")


if __name__ == "__main__":
    main()
