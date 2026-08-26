import { useState, useCallback } from 'react';
import type { Document, DocumentUploadResponse } from '@models';
import { documentService } from '@services/caseService';

interface UseDocumentsReturn {
  documents: Document[];
  loading: boolean;
  error: string | null;
  uploading: boolean;
  uploadProgress: number;
  
  listDocuments: () => Promise<void>;
  uploadDocument: (file: File) => Promise<DocumentUploadResponse | null>;
  deleteDocument: (docId: string) => Promise<boolean>;
  clearError: () => void;
}

/**
 * Hook for document management
 */
export const useDocuments = (): UseDocumentsReturn => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const listDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await documentService.listDocuments();
      setDocuments(response.documents);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load documents';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const uploadDocument = useCallback(async (file: File) => {
    try {
      setUploading(true);
      setError(null);
      setUploadProgress(0);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const result = await documentService.uploadDocument(file);
      clearInterval(progressInterval);
      setUploadProgress(100);

      // Refresh documents list
      await listDocuments();

      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed';
      setError(message);
      return null;
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  }, [listDocuments]);

  const deleteDocument = useCallback(async (docId: string) => {
    try {
      setError(null);
      await documentService.deleteDocument(docId);
      setDocuments(prev => prev.filter(doc => doc.doc_id !== docId));
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Delete failed';
      setError(message);
      return false;
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    documents,
    loading,
    error,
    uploading,
    uploadProgress,
    listDocuments,
    uploadDocument,
    deleteDocument,
    clearError,
  };
};
