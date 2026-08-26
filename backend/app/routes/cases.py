"""Case information API routes."""

import logging
from fastapi import APIRouter, HTTPException, Query
from uuid import UUID
from app.models.schemas import CaseDetail, CaseListResponse
from app.services.case_service import CaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cases", tags=["cases"])

# Global service instance
case_service: CaseService = None


def set_case_service(service: CaseService):
    """Set the case service instance."""
    global case_service
    case_service = service


@router.get("/{case_id}", response_model=CaseDetail)
async def get_case(case_id: str) -> CaseDetail:
    """Get case details by ID.
    
    Args:
        case_id: Case ID
        
    Returns:
        Full case details
    """
    try:
        if not case_service:
            raise HTTPException(status_code=500, detail="Case service not initialized")
        
        case = case_service.get_case(UUID(case_id))
        
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        return CaseDetail(
            case_id=str(case.case_id),
            title=case.title,
            year=case.year,
            judge=case.judge,
            decision=case.decision,
            case_text=case.case_text,
            court=case.court,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
    
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    except Exception as e:
        logger.error(f"Get case error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=CaseListResponse)
async def list_cases(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> CaseListResponse:
    """List all cases with pagination.
    
    Args:
        limit: Maximum number of cases to return
        offset: Result offset for pagination
        
    Returns:
        List of cases with pagination info
    """
    try:
        if not case_service:
            raise HTTPException(status_code=500, detail="Case service not initialized")
        
        cases, total = case_service.list_cases(limit=limit, offset=offset)
        
        case_details = [
            CaseDetail(
                case_id=str(case.case_id),
                title=case.title,
                year=case.year,
                judge=case.judge,
                decision=case.decision,
                case_text=case.case_text,
                court=case.court,
                created_at=case.created_at,
                updated_at=case.updated_at
            )
            for case in cases
        ]
        
        return CaseListResponse(
            cases=case_details,
            total=total,
            limit=limit,
            offset=offset
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List cases error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
