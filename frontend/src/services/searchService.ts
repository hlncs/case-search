import apiClient from './apiClient';
import type { SearchResponse } from '@models';

interface SearchRequest {
  query: string;
  limit?: number;
  offset?: number;
}

interface RAGQueryRequest {
  question: string;
  limit?: number;
  temperature?: number;
}

interface RAGQueryResponse {
  answer: string;
  sources: Array<{
    case_id: string;
    title: string;
    year: number;
    chunk_id?: string;
    relevance_score?: number;
  }>;
  model: string;
  chunks_used?: number;
  error?: string;
}

interface AgentQueryRequest {
  query: string;
  temperature?: number;
}

interface AgentQueryResponse {
  answer: string;
  reasoning_trace: Array<{
    step: number;
    action: string;
    input: string;
    result: Record<string, any>;
  }>;
  sources: Array<{
    case_id: string;
    title: string;
  }>;
  status: string;
  steps?: number;
  error?: string;
}

const AI_REQUEST_TIMEOUT_MS = 180000;

/**
 * Search service for case queries
 */
export const searchService = {
  /**
   * Standard vector search
   */
  async search(request: SearchRequest): Promise<SearchResponse> {
    return apiClient.post<SearchResponse>('/api/search', {
      query: request.query,
      limit: request.limit || 10,
      offset: request.offset || 0,
    });
  },

  /**
   * RAG-powered search (Retrieval-Augmented Generation)
   */
  async ragQuery(request: RAGQueryRequest): Promise<RAGQueryResponse> {
    return apiClient.post<RAGQueryResponse>(
      '/api/rag-query',
      {
        question: request.question,
        limit: request.limit || 5,
        temperature: request.temperature || 0.7,
      },
      { timeout: AI_REQUEST_TIMEOUT_MS }
    );
  },

  /**
   * Agent-powered query (Autonomous reasoning)
   */
  async agentQuery(request: AgentQueryRequest): Promise<AgentQueryResponse> {
    return apiClient.post<AgentQueryResponse>(
      '/api/agent-query',
      {
        query: request.query,
        temperature: request.temperature || 0.7,
      },
      { timeout: AI_REQUEST_TIMEOUT_MS }
    );
  },
};

export default searchService;
