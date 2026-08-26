"""Search service for vector-based semantic search."""

import logging
import re
from typing import List, Tuple
from uuid import UUID
from app.utils.embeddings import embed_text
from app.models.domain import SearchResult

logger = logging.getLogger(__name__)


class SearchService:
    """Service for vector search operations."""
    
    def __init__(self, document_repo=None):
        """Initialize search service.
        
        Args:
            document_repo: Document repository for querying embeddings
        """
        self.document_repo = document_repo
    
    def search(self, query: str, limit: int = 10, offset: int = 0) -> Tuple[List[SearchResult], int]:
        """Search for cases using semantic similarity.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            offset: Result offset for pagination
            
        Returns:
            Tuple of (results, total_count)
        """
        if not query or not query.strip():
            logger.warning("Empty search query")
            return [], 0
        
        logger.info(f"Searching for: {query}")
        
        # Generate embedding for query
        query_embedding = embed_text(query)
        
        # Search in vector store
        if self.document_repo:
            results, total = self.document_repo.search_similar(
                query_embedding, 
                limit=limit, 
                offset=offset
            )
            results = self._calibrate_relevance(query, results)
            logger.info(f"Found {total} results")
            return results, total
        
        return [], 0
    
    def get_embedding(self, text: str) -> list:
        """Get embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Vector embedding
        """
        return embed_text(text)

    def _calibrate_relevance(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        """Calibrate raw vector similarity into a more intuitive relevance score.

        Uses lexical overlap and exact-phrase matching as a tie-breaker/boost,
        especially useful for small corpora and local hashing embeddings.
        """
        query_normalized = self._normalize_text(query)
        query_tokens = self._tokenize(query_normalized)

        if not query_tokens:
            return results

        for result in results:
            raw_score = max(0.0, min(1.0, float(result.relevance_score)))
            text_normalized = self._normalize_text(result.decision or "")
            text_tokens = self._tokenize(text_normalized)

            overlap = 0.0
            if text_tokens:
                overlap = len(query_tokens & text_tokens) / len(query_tokens)

            contains_exact_phrase = (
                len(query_normalized) >= 20 and query_normalized in text_normalized
            )

            calibrated = (0.7 * raw_score) + (0.3 * overlap)

            if contains_exact_phrase:
                calibrated = max(calibrated, 0.9)
            elif overlap >= 0.8:
                calibrated = max(calibrated, 0.78)

            result.relevance_score = max(0.0, min(1.0, calibrated))

        return sorted(results, key=lambda item: item.relevance_score, reverse=True)

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", text))
