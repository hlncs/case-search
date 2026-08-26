import React, { useState } from 'react';
import { Container, Box, Typography, Alert, CircularProgress } from '@mui/material';
import SearchBar from '@components/SearchBar';
import ResultsList from '@components/ResultsList';
import { RAGResult, AgentResult } from '@components/AIResults';
import { useSearch } from '@hooks/useSearch';

type SearchMode = 'standard' | 'rag' | 'agent';

/**
 * Search page component
 */
const SearchPage: React.FC = () => {
  const [currentMode, setCurrentMode] = useState<SearchMode>('standard');
  const [currentPage, setCurrentPage] = useState(1);
  const [ragResult, setRagResult] = useState<any>(null);
  const [agentResult, setAgentResult] = useState<any>(null);
  const { results, total, loading, error, query, search } = useSearch();

  const handleModeChange = (mode: SearchMode) => {
    setCurrentMode(mode);
    setCurrentPage(1);
  };

  const handleSearchStart = (mode: SearchMode) => {
    if (mode === 'rag') {
      setRagResult(null);
    }
    if (mode === 'agent') {
      setAgentResult(null);
    }
    if (mode === 'standard') {
      setCurrentPage(1);
    }
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    const offset = (page - 1) * 10;
    search(query, 10, offset);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
          Legal Case Search
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Search for legal cases using vector similarity, RAG-powered analysis, or autonomous agents.
        </Typography>
      </Box>

      <SearchBar
        onModeChange={handleModeChange}
        onRagResult={setRagResult}
        onAgentResult={setAgentResult}
        onSearchStart={handleSearchStart}
      />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {currentMode === 'standard' && (
        <ResultsList
          results={results}
          total={total}
          loading={loading}
          error={error}
          query={query}
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      )}

      {currentMode === 'rag' && (
        <>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : ragResult ? (
            <RAGResult
              answer={ragResult.answer}
              sources={ragResult.sources}
              model={ragResult.model || 'llama3.2'}
              chunksUsed={ragResult.chunks_used}
            />
          ) : (
            <Box sx={{ py: 4, textAlign: 'center' }}>
              <Typography color="textSecondary">
                Enter a question to search using RAG
              </Typography>
            </Box>
          )}
        </>
      )}

      {currentMode === 'agent' && (
        <>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : agentResult ? (
            <AgentResult
              answer={agentResult.answer}
              reasoningTrace={agentResult.reasoning_trace}
              sources={agentResult.sources}
              status={agentResult.status}
              steps={agentResult.steps}
            />
          ) : (
            <Box sx={{ py: 4, textAlign: 'center' }}>
              <Typography color="textSecondary">
                Enter a query for the agent to research
              </Typography>
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default SearchPage;
