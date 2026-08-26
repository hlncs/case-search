from pydantic_settings import BaseSettings
from typing import Optional, List
import json
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://aiuser:aipassword@localhost:5432/ai"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Embeddings
    embedding_provider: str = "sentence-transformers"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_model_name: Optional[str] = None  # Alias for embedding_model
    embedding_model_path: Optional[str] = None
    embedding_dimension: int = 384
    ssl_ca_bundle: Optional[str] = None
    
    # File handling
    upload_dir: str = "./uploads"
    parquet_dir: str = "./data/parquet"
    max_upload_size: int = 52428800  # 50 MB
    
    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 100
    
    # RAG Configuration
    rag_max_chunks: int = 5
    rag_system_prompt: str = "You are a legal case analyst. Answer the user's question using only the provided case excerpts. Cite the case names and years."
    
    # Ollama LLM Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout: int = 120
    ollama_connect_timeout: int = 10
    ollama_read_timeout: int = 120
    ollama_num_predict: int = 256
    agent_temperature: float = 0.7
    
    # CORS Configuration
    cors_origins: str = '["http://localhost:5173", "http://localhost:3000"]'
    
    # Environment
    environment: str = "development"
    
    # Logging
    log_level: str = "INFO"
    
    # API
    api_title: str = "Legal Case Search API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from JSON string."""
        try:
            if isinstance(self.cors_origins, list):
                return self.cors_origins
            return json.loads(self.cors_origins)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()

if settings.ssl_ca_bundle:
    os.environ.setdefault("REQUESTS_CA_BUNDLE", settings.ssl_ca_bundle)
    os.environ.setdefault("SSL_CERT_FILE", settings.ssl_ca_bundle)
    os.environ.setdefault("CURL_CA_BUNDLE", settings.ssl_ca_bundle)
