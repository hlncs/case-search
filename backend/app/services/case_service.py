"""Case service for retrieving case information."""

import logging
from typing import List, Tuple
from uuid import UUID
from app.models.domain import Case

logger = logging.getLogger(__name__)


class CaseService:
    """Service for case data retrieval and management."""
    
    def __init__(self, case_repo=None):
        """Initialize case service.
        
        Args:
            case_repo: Case repository for database operations
        """
        self.case_repo = case_repo
    
    def get_case(self, case_id: UUID) -> Case:
        """Get case details by ID.
        
        Args:
            case_id: Case ID
            
        Returns:
            Case object
        """
        if self.case_repo:
            return self.case_repo.get_by_id(case_id)
        return None
    
    def list_cases(self, limit: int = 10, offset: int = 0) -> Tuple[List[Case], int]:
        """List all cases with pagination.
        
        Args:
            limit: Maximum number of cases
            offset: Result offset
            
        Returns:
            Tuple of (cases, total_count)
        """
        if self.case_repo:
            return self.case_repo.list_all(limit=limit, offset=offset)
        return [], 0
    
    def search_cases_by_year(self, year: int, limit: int = 10, offset: int = 0) -> Tuple[List[Case], int]:
        """Search cases by year.
        
        Args:
            year: Year to search
            limit: Maximum number of cases
            offset: Result offset
            
        Returns:
            Tuple of (cases, total_count)
        """
        if self.case_repo:
            return self.case_repo.search_by_year(year, limit=limit, offset=offset)
        return [], 0
    
    def create_case(self, case_data: dict) -> Case:
        """Create a new case.
        
        Args:
            case_data: Case information
            
        Returns:
            Created case object
        """
        if self.case_repo:
            return self.case_repo.create(case_data)
        return None
