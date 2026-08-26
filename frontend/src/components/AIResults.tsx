import React from 'react';
import {
  Paper,
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

interface RAGResultProps {
  answer: string;
  sources: Array<{
    case_id: string;
    title: string;
    year: number;
    chunk_id?: string;
    relevance_score?: number;
  }>;
  model: string;
  chunksUsed?: number;
}

/**
 * Component for displaying RAG results
 */
export const RAGResult: React.FC<RAGResultProps> = ({
  answer,
  sources,
  model,
  chunksUsed,
}) => {
  return (
    <Box sx={{ mb: 3 }}>
      <Paper elevation={2} sx={{ p: 3, mb: 2, backgroundColor: '#f5f5f5' }}>
        <Box sx={{ mb: 2 }}>
          <Chip label={`Model: ${model}`} size="small" variant="outlined" sx={{ mr: 1 }} />
          {chunksUsed && (
            <Chip label={`${chunksUsed} chunks used`} size="small" variant="outlined" />
          )}
        </Box>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Analysis
        </Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
          {answer}
        </Typography>
      </Paper>

      {sources.length > 0 && (
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
            Sources ({sources.length})
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ backgroundColor: '#f0f0f0' }}>
                  <TableCell>Case Title</TableCell>
                  <TableCell align="center">Year</TableCell>
                  <TableCell align="right">Relevance</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sources.map((source, idx) => (
                  <TableRow key={idx}>
                    <TableCell>{source.title}</TableCell>
                    <TableCell align="center">{source.year}</TableCell>
                    <TableCell align="right">
                      {source.relevance_score ? `${(source.relevance_score * 100).toFixed(1)}%` : '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  );
};

interface AgentResultProps {
  answer: string;
  reasoningTrace: Array<{
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
}

/**
 * Component for displaying Agent results
 */
export const AgentResult: React.FC<AgentResultProps> = ({
  answer,
  reasoningTrace,
  sources,
  status,
  steps,
}) => {
  return (
    <Box sx={{ mb: 3 }}>
      <Paper elevation={2} sx={{ p: 3, mb: 2, backgroundColor: '#f5f5f5' }}>
        <Box sx={{ mb: 2 }}>
          <Chip
            label={`Status: ${status}`}
            size="small"
            color={status === 'completed' ? 'success' : 'warning'}
            sx={{ mr: 1 }}
          />
          {steps && <Chip label={`${steps} steps`} size="small" variant="outlined" />}
        </Box>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Agent Response
        </Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
          {answer}
        </Typography>
      </Paper>

      {reasoningTrace.length > 0 && (
        <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
            Reasoning Trace ({reasoningTrace.length} steps)
          </Typography>
          {reasoningTrace.map((trace) => (
            <Accordion key={trace.step} defaultExpanded={trace.step === 1}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Step {trace.step}: {trace.action}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {trace.input && (
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="caption" color="textSecondary">
                      Input:
                    </Typography>
                    <Typography variant="body2">{trace.input}</Typography>
                  </Box>
                )}
                <Box>
                  <Typography variant="caption" color="textSecondary">
                    Result:
                  </Typography>
                  <Typography variant="body2" component="pre" sx={{ overflow: 'auto' }}>
                    {JSON.stringify(trace.result, null, 2)}
                  </Typography>
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </Paper>
      )}

      {sources.length > 0 && (
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
            Sources ({sources.length})
          </Typography>
          {sources.map((source, idx) => (
            <Card key={idx} sx={{ mb: 1 }}>
              <CardContent>
                <Typography variant="body2">{source.title}</Typography>
                <Typography variant="caption" color="textSecondary">
                  ID: {source.case_id}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Paper>
      )}
    </Box>
  );
};
