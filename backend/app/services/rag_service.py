"""RAG (Retrieval-Augmented Generation) service."""

import logging
from typing import List, Tuple, Optional
from app.config import settings
from app.services.search_service import SearchService
from app.services.llm_service import LLMService
from app.models.domain import SearchResult

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG pipeline: retrieve, augment, generate."""
    
    def __init__(self, search_service: SearchService = None, llm_service: LLMService = None):
        """Initialize RAG service.
        
        Args:
            search_service: Search service for retrieval
            llm_service: LLM service for generation
        """
        self.search_service = search_service or SearchService()
        self.llm_service = llm_service or LLMService()
    
    def rag_query(self, question: str, limit: int = 5, temperature: float = 0.7) -> dict:
        """Execute RAG pipeline: retrieve, augment, generate.
        
        Args:
            question: User question
            limit: Number of chunks to retrieve
            temperature: LLM temperature
            
        Returns:
            RAG response with answer and sources
        """
        try:
            logger.info(f"Starting RAG query: {question}")
            
            # Step 1: Retrieve relevant chunks
            results, total = self.search_service.search(question, limit=limit)
            logger.info(f"Retrieved {len(results)} relevant chunks")
            
            if not results:
                return {
                    "answer": "No relevant cases found for your question.",
                    "sources": [],
                    "model": settings.ollama_model,
                    "error": "No results"
                }
            
            # Step 2: Assemble context from retrieved chunks
            context = self._assemble_context(results)
            logger.info(f"Assembled context from {len(results)} chunks ({len(context)} characters)")
            
            # Step 3: Augment prompt with context
            augmented_prompt = self._create_augmented_prompt(question, context)
            
            # Step 4: Send to LLM for inference
            system_prompt = settings.rag_system_prompt or \
                "You are a legal case analyst. Answer the user's question using ONLY the provided case excerpts. Always cite the case names and years."
            
            answer = ""
            if self.llm_service.is_model_available():
                answer = self.llm_service.generate(
                    prompt=augmented_prompt,
                    system_prompt=system_prompt,
                    temperature=temperature
                )
            else:
                logger.warning(f"Ollama model {settings.ollama_model} is not available; using retrieved excerpts")
            if not answer.strip():
                answer = self._create_fallback_answer(question, results)
            
            logger.info(f"Generated RAG response ({len(answer)} characters)")
            
            # Step 5: Format sources with citations
            sources = [
                {
                    "case_id": str(result.case_id),
                    "title": result.title,
                    "year": result.year,
                    "chunk_id": str(result.matched_chunk_id) if result.matched_chunk_id else None,
                    "relevance_score": result.relevance_score
                }
                for result in results
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "model": settings.ollama_model,
                "chunks_used": len(results)
            }
        
        except Exception as e:
            logger.error(f"RAG query error: {str(e)}")
            return {
                "answer": f"Error processing RAG query: {str(e)}",
                "sources": [],
                "model": settings.ollama_model,
                "error": str(e)
            }
    
    def _assemble_context(self, results: List[SearchResult]) -> str:
        """Assemble context from retrieved results.
        
        Args:
            results: List of search results with chunks
            
        Returns:
            Combined context string
        """
        context_parts = []
        for i, result in enumerate(results, 1):
            # This would normally include the actual chunk text from the repository
            # For now, we include case metadata as context
            context_parts.append(
                f"Case {i}: {result.title} ({result.year})\n"
                f"Judge: {result.judge}\n"
                f"Decision: {result.decision}\n"
                f"Relevance: {result.relevance_score:.2%}\n"
            )
        
        return "\n".join(context_parts)
    
    def _create_fallback_answer(self, question: str, results: List[SearchResult]) -> str:
        """Create a grounded answer when the LLM is unavailable or returns no text."""
        lines = [
            f"I found {len(results)} relevant case excerpt(s) for: {question}",
            "",
        ]
        for index, result in enumerate(results, 1):
            lines.append(
                f"{index}. {result.title} ({result.year}) - relevance {result.relevance_score:.1%}\n"
                f"{result.decision}"
            )
        lines.append("")
        lines.append("The LLM did not return a generated answer, so this response shows the retrieved source excerpts directly.")
        return "\n\n".join(lines)
    
    def _create_augmented_prompt(self, question: str, context: str) -> str:
        """Create augmented prompt with context.
        
        Args:
            question: Original user question
            context: Retrieved context
            
        Returns:
            Augmented prompt for LLM
        """
        return f"""Based on the following legal cases, answer the user's question:

LEGAL CASES:
{context}

QUESTION: {question}

Please provide a comprehensive answer using ONLY the information from the cases above. Always cite the specific cases and years."""
