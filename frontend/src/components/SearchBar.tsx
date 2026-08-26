import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  Paper,
  CircularProgress,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useSearch } from '@hooks/useSearch';

type SearchMode = 'standard' | 'rag' | 'agent';

interface SearchBarProps {
  onModeChange?: (mode: SearchMode) => void;
  onRagResult?: (result: any) => void;
  onAgentResult?: (result: any) => void;
  onSearchStart?: (mode: SearchMode) => void;
}

/**
 * Search bar component with multiple search modes
 */
const SearchBar: React.FC<SearchBarProps> = ({
  onModeChange,
  onRagResult,
  onAgentResult,
  onSearchStart,
}) => {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<SearchMode>('standard');
  const { search, ragQuery, agentQuery, loading } = useSearch();

  const handleModeChange = (_: React.MouseEvent<HTMLElement>, newMode: SearchMode | null) => {
    if (newMode !== null) {
      setMode(newMode);
      onModeChange?.(newMode);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    onSearchStart?.(mode);

    switch (mode) {
      case 'rag':
        onRagResult?.(await ragQuery(query));
        break;
      case 'agent':
        onAgentResult?.(await agentQuery(query));
        break;
      case 'standard':
      default:
        await search(query);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleSearch();
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ mb: 2 }}>
        <ToggleButtonGroup
          value={mode}
          exclusive
          onChange={handleModeChange}
          size="small"
          sx={{ mb: 2 }}
        >
          <ToggleButton value="standard" aria-label="standard search">
            Standard
          </ToggleButton>
          <ToggleButton value="rag" aria-label="rag search">
            RAG
          </ToggleButton>
          <ToggleButton value="agent" aria-label="agent search">
            Agent
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Box sx={{ display: 'flex', gap: 2 }}>
        <TextField
          fullWidth
          placeholder={
            mode === 'rag'
              ? 'Ask a legal question...'
              : mode === 'agent'
              ? 'Complex legal research query...'
              : 'Search cases...'
          }
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
          variant="outlined"
          size="small"
          helperText={
            mode === 'rag'
              ? 'RAG: Retrieval-Augmented Generation for grounded answers'
              : mode === 'agent'
              ? 'Agent: Autonomous reasoning with tool usage'
              : 'Standard: Vector similarity search'
          }
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSearch}
          disabled={!query.trim() || loading}
          sx={{ minWidth: 120 }}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : <SearchIcon />}
        </Button>
      </Box>
    </Paper>
  );
};

export default SearchBar;
