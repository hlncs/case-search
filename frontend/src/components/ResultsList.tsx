import React from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Pagination,
  Container,
} from '@mui/material';
import CaseCard from './CaseCard';
import type { SearchResult } from '@models';
import { PAGINATION } from '@utils/constants';

interface ResultsListProps {
  results: SearchResult[];
  total: number;
  loading: boolean;
  error: string | null;
  query: string;
  currentPage?: number;
  onPageChange?: (page: number) => void;
  onDetailsClick?: (caseId: string) => void;
}

/**
 * Results list component with pagination
 */
const ResultsList: React.FC<ResultsListProps> = ({
  results,
  total,
  loading,
  error,
  query,
  currentPage = 1,
  onPageChange,
  onDetailsClick,
}) => {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!query) {
    return (
      <Box sx={{ py: 4, textAlign: 'center' }}>
        <Typography color="textSecondary">
          Enter a search query to get started
        </Typography>
      </Box>
    );
  }

  if (results.length === 0) {
    return (
      <Alert severity="info">
        No cases found for "{query}". Try a different search query.
      </Alert>
    );
  }

  const totalPages = Math.ceil(total / PAGINATION.PAGE_SIZE);

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" color="textSecondary">
          Found <strong>{total}</strong> result{total !== 1 ? 's' : ''} for "{query}"
        </Typography>
      </Box>

      <Box sx={{ mb: 3 }}>
        {results.map((result) => (
          <CaseCard
            key={result.case_id}
            result={result}
            onDetailsClick={onDetailsClick}
          />
        ))}
      </Box>

      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
          <Pagination
            count={totalPages}
            page={currentPage}
            onChange={(_, page) => onPageChange?.(page)}
            color="primary"
          />
        </Box>
      )}
    </Container>
  );
};

export default ResultsList;
