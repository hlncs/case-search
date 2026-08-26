import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  LinearProgress,
  CircularProgress,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import { useDocuments } from '@hooks/useDocuments';
import { formatDate } from '@utils/formatting';

/**
 * Upload page component for document management
 */
const UploadPage: React.FC = () => {
  const {
    documents,
    loading,
    error,
    uploading,
    uploadProgress,
    listDocuments,
    uploadDocument,
    deleteDocument,
    clearError,
  } = useDocuments();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);

  React.useEffect(() => {
    listDocuments();
  }, []);

  const handleFilePick = (file: File | undefined) => {
    if (file) {
      const validTypes = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf', 'text/plain'];
      if (validTypes.includes(file.type) || file.name.endsWith('.docx') || file.name.endsWith('.pdf') || file.name.endsWith('.txt')) {
        setSelectedFile(file);
        setUploadSuccess(false);
      } else {
        alert('Please select a .docx, .pdf, or .txt file');
      }
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFilePick(event.target.files?.[0]);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragActive(true);
  };

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragActive(false);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragActive(false);

    const file = event.dataTransfer.files?.[0];
    handleFilePick(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const result = await uploadDocument(selectedFile);
    if (result) {
      setUploadSuccess(true);
      setSelectedFile(null);
      const input = document.getElementById('file-input') as HTMLInputElement;
      if (input) input.value = '';
      setTimeout(() => setUploadSuccess(false), 5000);
    }
  };

  const handleDeleteClick = (docId: string) => {
    setDocToDelete(docId);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (docToDelete) {
      await deleteDocument(docToDelete);
      setDeleteDialogOpen(false);
      setDocToDelete(null);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
          Document Upload
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Upload legal documents to build your searchable case database.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" onClose={clearError} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {uploadSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Document uploaded and indexed successfully!
        </Alert>
      )}

      {/* Upload Section */}
      <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
        <Box
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          sx={{
            border: '2px dashed #1976d2',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            backgroundColor: isDragActive ? '#e3f2fd' : '#f5f5f5',
            cursor: 'pointer',
            transition: 'all 0.3s',
            '&:hover': {
              backgroundColor: '#e8f4f8',
              borderColor: '#1565c0',
            },
            ...(isDragActive && {
              borderColor: '#0d47a1',
              boxShadow: '0 0 0 4px rgba(25, 118, 210, 0.16)',
            }),
          }}
        >
          <input
            id="file-input"
            type="file"
            accept=".docx,.pdf,.txt"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-input" style={{ cursor: 'pointer', display: 'block' }}>
            <CloudUploadIcon sx={{ fontSize: 48, color: '#1976d2', mb: 2 }} />
            <Typography variant="h6" sx={{ mb: 1 }}>
              Drop files here or click to select
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: .docx, .pdf, .txt
            </Typography>
            {selectedFile && (
              <Typography variant="body2" sx={{ mt: 2, color: '#388e3c', fontWeight: 600 }}>
                Selected: {selectedFile.name}
              </Typography>
            )}
          </label>
        </Box>

        {uploading && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <CircularProgress size={24} />
              <Typography variant="body2">Uploading and processing document...</Typography>
            </Box>
            <LinearProgress variant="determinate" value={uploadProgress} />
          </Box>
        )}

        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
          >
            Upload Document
          </Button>
          <Button
            variant="outlined"
            onClick={() => {
              setSelectedFile(null);
              const input = document.getElementById('file-input') as HTMLInputElement;
              if (input) input.value = '';
            }}
            disabled={!selectedFile || uploading}
          >
            Clear Selection
          </Button>
        </Box>
      </Paper>

      {/* Documents List */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Uploaded Documents ({documents.length})
        </Typography>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : documents.length === 0 ? (
        <Alert severity="info">
          No documents uploaded yet. Upload your first document to get started.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f0f0f0' }}>
                <TableCell>Filename</TableCell>
                <TableCell align="center">Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Uploaded</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.map((doc) => (
                <TableRow key={doc.doc_id}>
                  <TableCell>{doc.filename}</TableCell>
                  <TableCell align="center">{doc.file_type}</TableCell>
                  <TableCell>
                    <Box
                      sx={{
                        display: 'inline-block',
                        px: 1.5,
                        py: 0.5,
                        borderRadius: 1,
                        backgroundColor:
                          doc.status === 'indexed'
                            ? '#e8f5e9'
                            : doc.status === 'processing'
                            ? '#fff3e0'
                            : '#ffebee',
                        color:
                          doc.status === 'indexed'
                            ? '#2e7d32'
                            : doc.status === 'processing'
                            ? '#e65100'
                            : '#c62828',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                      }}
                    >
                      {doc.status}
                    </Box>
                  </TableCell>
                  <TableCell>{formatDate(doc.uploaded_at)}</TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDeleteClick(doc.doc_id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Document</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this document? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default UploadPage;
