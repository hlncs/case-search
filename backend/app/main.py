"""FastAPI application entry point."""

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.logger import setup_logging
from app.models.schemas import HealthResponse
from app.services.search_service import SearchService
from app.services.document_service import DocumentService
from app.services.case_service import CaseService
from app.services.rag_service import RAGService
from app.services.agent_service import AgentService
from app.services.llm_service import LLMService
from app.repositories.postgres_repository import PostgresDocumentRepository
from app.routes import search, documents, cases, rag_agents

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting up application")
    document_repo = PostgresDocumentRepository()
    document_repo.initialize_schema()
    
    # Initialize core services
    search_service = SearchService(document_repo=document_repo)
    document_service = DocumentService(document_repo=document_repo)
    case_service = CaseService(case_repo=document_repo)
    
    # Initialize LLM and advanced services
    llm_service = LLMService()
    rag_service = RAGService(search_service=search_service, llm_service=llm_service)
    agent_service = AgentService(
        search_service=search_service,
        case_service=case_service,
        llm_service=llm_service
    )
    
    # Inject services into routes
    search.set_search_service(search_service)
    documents.set_document_service(document_service)
    cases.set_case_service(case_service)
    rag_agents.set_rag_service(rag_service)
    rag_agents.set_agent_service(agent_service)
    
    # Check Ollama availability
    if llm_service.is_available():
        logger.info(f"Ollama service is available at {settings.ollama_base_url}")
    else:
        logger.warning(f"Ollama service not available at {settings.ollama_base_url}")
    
    logger.info("Services initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application")


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow()
    )


# Include route routers
app.include_router(search.router)
app.include_router(documents.router)
app.include_router(cases.router)
app.include_router(rag_agents.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
