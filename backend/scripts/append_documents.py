#!/usr/bin/env python3
"""
Append new documents to the existing index.

This script processes only NEW .docx files from the cases/ folder,
skipping those already processed in previous runs.

Usage:
    source venv/bin/activate
    python scripts/append_documents.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.utils.parsers import parse_document, chunk_text
from app.repositories.postgres_repository import PostgresDocumentRepository
from init_documents import process_document_file as process_document_for_postgres
from init_documents import save_to_postgres
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Index tracking file
INDEX_FILE = Path("data/documents/index.json")


def load_index() -> dict:
    """Load the index of already-processed documents."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    return {"processed_files": {}, "last_updated": None}


def save_index(index: dict):
    """Save the index of processed documents."""
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    index["last_updated"] = datetime.now().isoformat()
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    logger.info(f"Updated index: {INDEX_FILE}")


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
    
    logger.info(f"Found {len(docx_files)} total .docx files in {cases_dir}")
    return sorted(docx_files)


def get_new_documents(all_files: list[Path], index: dict) -> list[Path]:
    """Filter to only new documents not yet processed."""
    processed = set(index.get("processed_files", {}).keys())
    new_files = [f for f in all_files if f.name not in processed]
    return new_files


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
            "doc_id": doc_id,
            "filename": file_path.name,
            "file_type": "docx",
            "chunks": len(chunks),
            "content_length": len(text_content),
            "chunks_text": chunks,
        }
    
    except Exception as e:
        logger.error(f"  ✗ Error processing {file_path.name}: {str(e)}")
        return {"status": "failed", "reason": str(e)}


def save_to_file_storage(doc_id: str, content: str, chunks: list):
    """Save document metadata and chunks to JSON for manual storage."""
    storage_dir = Path("data/documents")
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Save metadata
    metadata_file = storage_dir / f"{doc_id}_metadata.json"
    metadata = {
        "doc_id": doc_id,
        "num_chunks": len(chunks),
        "content_length": len(content),
        "chunks": chunks,
        "saved_at": datetime.now().isoformat(),
    }
    
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"  Saved metadata to {metadata_file}")
    
    return str(metadata_file)


def main():
    """Main append function."""
    logger.info("=" * 70)
    logger.info("LEGAL CASE SEARCH - Append New Documents")
    logger.info("=" * 70)
    
    # Get the project root (parent of backend directory)
    project_root = Path(__file__).parent.parent.parent
    cases_dir = project_root / "cases"

    document_repo = PostgresDocumentRepository()
    document_repo.initialize_schema()
    existing_documents, _ = document_repo.list_documents()
    processed_filenames = {document.filename for document in existing_documents}
    logger.info(f"PostgreSQL already contains {len(processed_filenames)} document(s)")
    
    # Get all documents
    all_files = get_valid_documents(str(cases_dir))
    if not all_files:
        logger.error("No .docx files found")
        return
    
    # Get new documents
    new_files = [doc_file for doc_file in all_files if doc_file.name not in processed_filenames]
    
    logger.info(f"\n{'New Documents to Process':^70}")
    logger.info("-" * 70)
    
    if not new_files:
        logger.info("No new documents found. PostgreSQL is up to date.")
        logger.info(f"Already processed: {len(processed_filenames)} files")
        return
    
    logger.info(f"Found {len(new_files)} new document(s) to process")
    
    results = {
        "total": len(new_files),
        "successful": 0,
        "failed": 0,
        "documents": [],
    }
    
    # Process each new document
    for doc_file in new_files:
        result = process_document_for_postgres(doc_file)
        
        if result["status"] == "success":
            results["successful"] += 1
            results["documents"].append(result)
            save_to_postgres(document_repo, result)
        else:
            results["failed"] += 1
            logger.error(f"Failed to process {doc_file.name}: {result.get('reason', 'Unknown error')}")
    
    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("APPEND SUMMARY")
    logger.info("=" * 70)
    logger.info(f"New files processed: {results['total']}")
    logger.info(f"Successful: {results['successful']} ✓")
    logger.info(f"Failed: {results['failed']} ✗")
    logger.info(f"Total in PostgreSQL: {len(processed_filenames) + results['successful']} files")
    
    if results["successful"] > 0:
        logger.info("\nNew documents added to PostgreSQL:")
        for doc in results["documents"]:
            logger.info(f"  • {doc['filename']}")
            logger.info(f"    ID: {doc['doc_id']}")
            logger.info(f"    Chunks: {doc['chunks']}")
            logger.info(f"    Content: {doc['content_length']} chars")
    
    logger.info("\n" + "=" * 70)
    logger.info("Run python scripts/verify_embeddings.py to verify database embeddings")
    logger.info("=" * 70 + "\n")


if __name__ == "__main__":
    main()
