import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Chip,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useCaseDetail } from '@hooks/useCaseDetail';
import { formatDate } from '@utils/formatting';

/**
 * Case detail page component
 */
const CaseDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const { caseDetail, loading, error, clearError } = useCaseDetail(caseId);

  if (!caseId) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">Case ID not provided</Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" onClose={clearError}>
          {error}
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(-1)}
          sx={{ mt: 2 }}
        >
          Go Back
        </Button>
      </Container>
    );
  }

  if (!caseDetail) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="info">Case not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate(-1)}
        sx={{ mb: 3 }}
      >
        Back to Results
      </Button>

      <Paper elevation={2} sx={{ p: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
            <Typography variant="h4" sx={{ fontWeight: 600, flex: 1 }}>
              {caseDetail.title}
            </Typography>
            <Chip label={`${caseDetail.year}`} color="primary" variant="outlined" />
          </Box>

          <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
            Court: <strong>{caseDetail.court}</strong>
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Judge: <strong>{caseDetail.judge}</strong>
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Decision
          </Typography>
          <Paper elevation={0} sx={{ p: 2, backgroundColor: '#f9f9f9' }}>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
              {caseDetail.decision}
            </Typography>
          </Paper>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Box>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Full Case Text
          </Typography>
          <Paper elevation={0} sx={{ p: 2, backgroundColor: '#f9f9f9' }}>
            <Typography
              variant="body2"
              sx={{
                whiteSpace: 'pre-wrap',
                lineHeight: 1.8,
                maxHeight: 600,
                overflow: 'auto',
                fontFamily: 'monospace',
                fontSize: '0.85rem',
              }}
            >
              {caseDetail.case_text}
            </Typography>
          </Paper>
        </Box>

        <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid #eee' }}>
          <Typography variant="caption" color="textSecondary">
            Created: {formatDate(caseDetail.created_at)} | Updated: {formatDate(caseDetail.updated_at)}
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default CaseDetailPage;
