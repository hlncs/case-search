// TypeScript interfaces for frontend models.

export interface Case {
  case_id: string;
  title: string;
  year: number;
  judge: string;
  decision: string;
  case_text: string;
  court: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  doc_id: string;
  filename: string;
  file_type: string;
  uploaded_at: string;
  status: string;
}

export interface SearchResult {
  case_id: string;
  title: string;
  year: number;
  judge: string;
  decision: string;
  relevance_score: number;
  matched_chunk_id?: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  limit: number;
  offset: number;
}

export interface DocumentUploadResponse {
  doc_id: string;
  filename: string;
  file_type: string;
  status: string;
  message: string;
}
