import React, { createContext, useContext, useState, useCallback } from 'react';
import type { SearchResult } from '@models';
import searchService from '@services/searchService';

interface SearchContextType {
  results: SearchResult[];
  total: number;
  loading: boolean;
  error: string | null;
  query: string;
  offset: number;
  
  search: (query: string, limit?: number, offset?: number) => Promise<void>;
  ragQuery: (question: string, limit?: number) => Promise<any>;
  agentQuery: (query: string) => Promise<any>;
  clearResults: () => void;
  setOffset: (offset: number) => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [offset, setOffset] = useState(0);

  const search = useCallback(async (q: string, limit = 10, off = 0) => {
    try {
      setLoading(true);
      setError(null);
      setQuery(q);
      setOffset(off);
      
      const response = await searchService.search({
        query: q,
        limit,
        offset: off,
      });
      
      setResults(response.results);
      setTotal(response.total);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Search failed';
      setError(message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const ragQuery = useCallback(async (question: string, limit = 5) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await searchService.ragQuery({
        question,
        limit,
      });
      
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'RAG query failed';
      setError(message);
      return { answer: '', sources: [] };
    } finally {
      setLoading(false);
    }
  }, []);

  const agentQuery = useCallback(async (q: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await searchService.agentQuery({ query: q });
      
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Agent query failed';
      setError(message);
      return { answer: '', reasoning_trace: [], sources: [] };
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults([]);
    setTotal(0);
    setQuery('');
    setOffset(0);
    setError(null);
  }, []);

  const value: SearchContextType = {
    results,
    total,
    loading,
    error,
    query,
    offset,
    search,
    ragQuery,
    agentQuery,
    clearResults,
    setOffset,
  };

  return (
    <SearchContext.Provider value={value}>
      {children}
    </SearchContext.Provider>
  );
};

export const useSearch = () => {
  const context = useContext(SearchContext);
  if (!context) {
    throw new Error('useSearch must be used within SearchProvider');
  }
  return context;
};
