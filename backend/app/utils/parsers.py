"""Document parsing utilities for .docx, .pdf, and .txt files."""

import logging
from pathlib import Path
from typing import List, Tuple
import pdfplumber
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)


def parse_docx(file_path: str) -> str:
    """Parse .docx file and extract text."""
    try:
        doc = DocxDocument(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error parsing DOCX file {file_path}: {str(e)}")
        raise


def parse_pdf(file_path: str) -> str:
    """Parse .pdf file and extract text."""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error parsing PDF file {file_path}: {str(e)}")
        raise


def parse_txt(file_path: str) -> str:
    """Parse .txt file and extract text."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    except Exception as e:
        logger.error(f"Error parsing TXT file {file_path}: {str(e)}")
        raise


def parse_document(file_path: str) -> str:
    """Parse document based on file extension."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == ".docx":
        return parse_docx(file_path)
    elif suffix == ".pdf":
        return parse_pdf(file_path)
    elif suffix == ".txt":
        return parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Approximate tokens per chunk
        overlap: Tokens to overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Simple word-based chunking (approximate tokens)
    words = text.split()
    chunks = []
    
    words_per_chunk = max(1, chunk_size // 4)  # Approximate: 4 chars per token
    overlap_words = max(1, overlap // 4)
    
    start = 0
    while start < len(words):
        end = min(start + words_per_chunk, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += words_per_chunk - overlap_words
    
    return chunks
