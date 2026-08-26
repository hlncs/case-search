import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
  Chip,
  LinearProgress,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { SearchResult } from '@models';
import { formatRelevanceScore, truncateText } from '@utils/formatting';

interface CaseCardProps {
  result: SearchResult;
  onDetailsClick?: (caseId: string) => void;
}

/**
 * Card component for displaying a case result
 */
const CaseCard: React.FC<CaseCardProps> = ({ result, onDetailsClick }) => {
  const handleDetailsClick = () => {
    onDetailsClick?.(result.case_id);
  };

  return (
    <Card sx={{ mb: 2, '&:hover': { boxShadow: 4 } }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
          <Typography variant="h6" component="h3" sx={{ flex: 1 }}>
            {result.title}
          </Typography>
          <Box sx={{ ml: 2, whiteSpace: 'nowrap' }}>
            <Chip
              label={`${result.year}`}
              variant="outlined"
              size="small"
              color="primary"
            />
          </Box>
        </Box>

        <Box sx={{ mb: 2, display: 'flex', gap: 1, alignItems: 'center' }}>
          <Typography variant="body2" color="textSecondary">
            Judge: <strong>{result.judge}</strong>
          </Typography>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <Typography variant="caption" color="textSecondary">
              Relevance Score
            </Typography>
            <Typography variant="caption" color="primary" sx={{ fontWeight: 600 }}>
              {formatRelevanceScore(result.relevance_score)}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={result.relevance_score * 100}
            sx={{ height: 4, borderRadius: 2 }}
          />
        </Box>

        <Typography variant="body2" sx={{ mb: 1 }}>
          {truncateText(result.decision, 200)}
        </Typography>
      </CardContent>

      <CardActions>
        <Button
          size="small"
          color="primary"
          component={RouterLink}
          to={`/cases/${result.case_id}`}
          onClick={handleDetailsClick}
        >
          View Details
        </Button>
      </CardActions>
    </Card>
  );
};

export default CaseCard;
