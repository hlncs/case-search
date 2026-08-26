import apiClient from './apiClient';
import type { Case, Document, DocumentUploadResponse } from '@models';

interface CaseListResponse {
  cases: Case[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Case service for case queries
 */
export const caseService = {
  /**
   * Get case by ID
   */
  async getCase(caseId: string): Promise<Case> {
    return apiClient.get<Case>(`/api/cases/${caseId}`);
  },

  /**
   * List all cases with pagination
   */
  async listCases(limit: number = 10, offset: number = 0): Promise<CaseListResponse> {
    return apiClient.get<CaseListResponse>(`/api/cases?limit=${limit}&offset=${offset}`);
  },
};

/**
 * Document service for document management
 */
export const documentService = {
  /**
   * Upload a document
   */
  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    return apiClient.uploadFile<DocumentUploadResponse>('/api/documents/upload', file);
  },

  /**
   * List all documents
   */
  async listDocuments(): Promise<{ documents: Document[]; total: number }> {
    return apiClient.get('/api/documents');
  },

  /**
   * Delete a document
   */
  async deleteDocument(docId: string): Promise<{ message: string }> {
    return apiClient.delete(`/api/documents/${docId}`);
  },
};

export default { caseService, documentService };
