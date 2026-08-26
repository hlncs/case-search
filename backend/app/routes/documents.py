"""Document management API routes."""

import logging
import os
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from uuid import UUID
from app.config import settings
from app.models.schemas import DocumentUploadResponse, DocumentListResponse, DocumentMetadata
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Global service instance
document_service: DocumentService = None


def set_document_service(service: DocumentService):
    """Set the document service instance."""
    global document_service
    document_service = service


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    """Upload and process a document.
    
    Args:
        file: File to upload (.docx, .pdf, or .txt)
        
    Returns:
        Upload result with document ID and status
    """
    file_path = None
    try:
        if not document_service:
            raise HTTPException(status_code=500, detail="Document service not initialized")
        
        # Validate file type
        allowed_extensions = ['.docx', '.pdf', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file
        file_path = os.path.join(settings.upload_dir, file.filename)
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved uploaded file: {file_path}")
        
        # Process document
        result = document_service.process_uploaded_file(file_path)
        
        return DocumentUploadResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


@router.get("", response_model=DocumentListResponse)
async def list_documents() -> DocumentListResponse:
    """List uploaded documents.
    
    Returns:
        List of documents with metadata
    """
    try:
        if not document_service:
            raise HTTPException(status_code=500, detail="Document service not initialized")
        
        documents_list, total = document_service.list_documents()
        return DocumentListResponse(
            documents=[
                DocumentMetadata(
                    doc_id=str(document.doc_id),
                    filename=document.filename,
                    file_type=document.file_type,
                    uploaded_at=document.uploaded_at,
                    status=document.status,
                )
                for document in documents_list
            ],
            total=total,
        )
    
    except Exception as e:
        logger.error(f"List documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(doc_id: str) -> JSONResponse:
    """Delete a document.
    
    Args:
        doc_id: Document ID to delete
        
    Returns:
        Deletion status
    """
    try:
        if not document_service:
            raise HTTPException(status_code=500, detail="Document service not initialized")
        
        success = document_service.delete_document(UUID(doc_id))
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found or could not be deleted")
        
        return JSONResponse({"message": f"Document {doc_id} deleted successfully"})
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        logger.error(f"Delete document error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
