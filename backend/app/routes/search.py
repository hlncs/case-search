"""Search API routes."""

import logging
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import SearchRequest, SearchResponse, SearchResultItem
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])

# Global service instance (will be injected via dependency)
search_service: SearchService = None


def set_search_service(service: SearchService):
    """Set the search service instance."""
    global search_service
    search_service = service


@router.post("", response_model=SearchResponse)
async def search_cases(request: SearchRequest) -> SearchResponse:
    """Search for legal cases using semantic similarity.
    
    Args:
        request: Search request with query, limit, and offset
        
    Returns:
        Search results with case metadata and relevance scores
    """
    try:
        if not search_service:
            raise HTTPException(status_code=500, detail="Search service not initialized")
        
        results, total = search_service.search(
            query=request.query,
            limit=request.limit,
            offset=request.offset
        )
        
        # Convert results to response format
        result_items = [
            SearchResultItem(
                case_id=str(result.case_id),
                title=result.title,
                year=result.year,
                judge=result.judge,
                decision=result.decision,
                relevance_score=result.relevance_score,
                matched_chunk_id=str(result.matched_chunk_id) if result.matched_chunk_id else None
            )
            for result in results
        ]
        
        return SearchResponse(
            results=result_items,
            total=total,
            limit=request.limit,
            offset=request.offset
        )
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
