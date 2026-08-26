"""RAG and Agent API routes."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.rag_service import RAGService
from app.services.agent_service import AgentService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rag-agents"])

# Global service instances
rag_service: RAGService = None
agent_service: AgentService = None


def set_rag_service(service: RAGService):
    """Set the RAG service instance."""
    global rag_service
    rag_service = service


def set_agent_service(service: AgentService):
    """Set the agent service instance."""
    global agent_service
    agent_service = service


# Request/Response models
class RAGQueryRequest(BaseModel):
    """RAG query request."""
    question: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(5, ge=1, le=20)
    temperature: float = Field(0.7, ge=0.0, le=1.0)


class SourceCitation(BaseModel):
    """Source citation for answer."""
    case_id: str
    title: str
    year: int
    chunk_id: Optional[str] = None
    relevance_score: float = 0.0


class RAGQueryResponse(BaseModel):
    """RAG query response."""
    answer: str
    sources: List[SourceCitation]
    model: str
    chunks_used: Optional[int] = None
    error: Optional[str] = None


class AgentQueryRequest(BaseModel):
    """Agent query request."""
    query: str = Field(..., min_length=1, max_length=2000)
    temperature: float = Field(0.7, ge=0.0, le=1.0)


class ReasoningStep(BaseModel):
    """Single step in agent reasoning trace."""
    step: int
    action: str
    input: str = ""
    result: dict


class AgentQueryResponse(BaseModel):
    """Agent query response."""
    answer: str
    reasoning_trace: List[ReasoningStep]
    sources: List[SourceCitation]
    status: str
    steps: Optional[int] = None
    error: Optional[str] = None


# RAG endpoints
@router.post("/api/rag-query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest) -> RAGQueryResponse:
    """Execute RAG pipeline query.
    
    Retrieves relevant case chunks, augments with LLM prompt,
    and returns grounded answer backed by citations.
    
    Args:
        request: RAG query with question and parameters
        
    Returns:
        RAG response with answer and source citations
    """
    try:
        if not rag_service:
            raise HTTPException(status_code=500, detail="RAG service not initialized")
        
        result = rag_service.rag_query(
            question=request.question,
            limit=request.limit,
            temperature=request.temperature
        )
        
        # Convert sources to proper format
        sources = [
            SourceCitation(
                case_id=source["case_id"],
                title=source["title"],
                year=source["year"],
                chunk_id=source.get("chunk_id"),
                relevance_score=source.get("relevance_score", 0.0)
            )
            for source in result.get("sources", [])
        ]
        
        return RAGQueryResponse(
            answer=result.get("answer", ""),
            sources=sources,
            model=result.get("model", "unknown"),
            chunks_used=result.get("chunks_used"),
            error=result.get("error")
        )
    
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent endpoints
@router.post("/api/agent-query", response_model=AgentQueryResponse)
async def agent_query(request: AgentQueryRequest) -> AgentQueryResponse:
    """Execute autonomous agent query.
    
    Agent uses tools to search, retrieve, and analyze cases,
    then synthesizes comprehensive answer with reasoning trace.
    
    Args:
        request: Agent query with question
        
    Returns:
        Agent response with answer, reasoning, and sources
    """
    try:
        if not agent_service:
            raise HTTPException(status_code=500, detail="Agent service not initialized")
        
        result = agent_service.run(request.query)
        
        # Convert reasoning trace
        reasoning_trace = [
            ReasoningStep(
                step=trace["step"],
                action=trace["action"],
                input=trace.get("input", ""),
                result=trace.get("result", {})
            )
            for trace in result.get("reasoning_trace", [])
        ]
        
        # Convert sources
        sources = [
            SourceCitation(
                case_id=source.get("case_id", ""),
                title=source.get("title", ""),
                year=source.get("year", 0)
            )
            for source in result.get("sources", [])
        ]
        
        return AgentQueryResponse(
            answer=result.get("answer", ""),
            reasoning_trace=reasoning_trace,
            sources=sources,
            status=result.get("status", "unknown"),
            steps=result.get("steps"),
            error=result.get("error")
        )
    
    except Exception as e:
        logger.error(f"Agent query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
