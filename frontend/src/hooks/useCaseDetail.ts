import { useState, useCallback, useEffect } from 'react';
import type { Case } from '@models';
import { caseService } from '@services/caseService';

interface UseCaseDetailReturn {
  caseDetail: Case | null;
  loading: boolean;
  error: string | null;
  
  fetchCase: (caseId: string) => Promise<void>;
  clearError: () => void;
}

/**
 * Hook for fetching and managing case details
 */
export const useCaseDetail = (caseId?: string): UseCaseDetailReturn => {
  const [caseDetail, setCaseDetail] = useState<Case | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCase = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      const result = await caseService.getCase(id);
      setCaseDetail(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch case';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Auto-fetch if caseId is provided
  useEffect(() => {
    if (caseId) {
      fetchCase(caseId);
    }
  }, [caseId, fetchCase]);

  return {
    caseDetail,
    loading,
    error,
    fetchCase,
    clearError,
  };
};
