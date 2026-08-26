"""Embedding model utilities."""

from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import normalize

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None

from app.config import settings
import logging

logger = logging.getLogger(__name__)

_model = None
_hashing_vectorizer: Optional[HashingVectorizer] = None


def _get_hashing_vectorizer() -> HashingVectorizer:
    """Get a stateless local embedding vectorizer."""
    global _hashing_vectorizer
    if _hashing_vectorizer is None:
        _hashing_vectorizer = HashingVectorizer(
            n_features=settings.embedding_dimension,
            alternate_sign=False,
            norm=None,
        )
    return _hashing_vectorizer


def _embed_with_hashing(texts: list[str]) -> list[list[float]]:
    """Generate local fixed-size vectors without external model downloads."""
    vectorizer = _get_hashing_vectorizer()
    matrix = vectorizer.transform(texts)
    matrix = normalize(matrix, norm="l2", axis=1)
    dense_matrix = matrix.astype(np.float32).toarray()
    return dense_matrix.tolist()


def _get_model_name_or_path() -> str:
    """Resolve configured embedding model, preferring a local path when provided."""
    if settings.embedding_model_path:
        model_path = Path(settings.embedding_model_path)
        if model_path.exists():
            return str(model_path)
        raise FileNotFoundError(
            f"EMBEDDING_MODEL_PATH is set to '{settings.embedding_model_path}', "
            "but that path does not exist. Download or copy the model there, "
            "or remove EMBEDDING_MODEL_PATH to load from Hugging Face."
        )
    return settings.embedding_model


def get_embedding_model() -> 'SentenceTransformer':
    """Get or load the embedding model."""
    global _model
    if not HAS_SENTENCE_TRANSFORMERS:
        raise ImportError(
            "sentence_transformers is required for embeddings. "
            "Install with: pip install sentence-transformers"
        )
    if _model is None:
        model_name_or_path = _get_model_name_or_path()
        logger.info(f"Loading embedding model: {model_name_or_path}")
        try:
            _model = SentenceTransformer(model_name_or_path)
        except Exception as exc:
            raise RuntimeError(
                "Could not load embedding model. If Hugging Face is blocked by "
                "your network, download the model on an approved network, copy it "
                "to backend/data/models/all-MiniLM-L6-v2, and set "
                "EMBEDDING_MODEL_PATH=./data/models/all-MiniLM-L6-v2 in backend/.env. "
                "If the error is certificate-related, ensure SSL_CA_BUNDLE points "
                "to /etc/ssl/certs/ca-certificates.crt."
            ) from exc
        logger.info("Embedding model loaded successfully")
    return _model


def embed_text(text: str) -> list:
    """Generate embedding for text."""
    try:
        if settings.embedding_provider == "hashing":
            embedding = _embed_with_hashing([text])[0]
            logger.info(
                "Embedding retrieval successful: provider=hashing dim=%d text_len=%d",
                len(embedding),
                len(text),
            )
            return embedding

        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError(
                "sentence_transformers is required for embeddings. "
                "Install with: pip install sentence-transformers"
            )

        model = get_embedding_model()
        embedding = model.encode(text, convert_to_tensor=False).tolist()
        logger.info(
            "Embedding retrieval successful: provider=sentence-transformers dim=%d text_len=%d",
            len(embedding),
            len(text),
        )
        return embedding
    except Exception as exc:
        logger.error("Embedding retrieval failed for single text: %s", str(exc))
        raise


def embed_batch(texts: list) -> list:
    """Generate embeddings for multiple texts."""
    try:
        if settings.embedding_provider == "hashing":
            embeddings = _embed_with_hashing(texts)
            logger.info(
                "Embedding retrieval successful: provider=hashing batch_size=%d dim=%d",
                len(embeddings),
                len(embeddings[0]) if embeddings else 0,
            )
            return embeddings

        model = get_embedding_model()
        embeddings = model.encode(texts, convert_to_tensor=False)
        result = [emb.tolist() for emb in embeddings]
        logger.info(
            "Embedding retrieval successful: provider=sentence-transformers batch_size=%d dim=%d",
            len(result),
            len(result[0]) if result else 0,
        )
        return result
    except Exception as exc:
        logger.error(
            "Embedding retrieval failed for batch: size=%d error=%s",
            len(texts),
            str(exc),
        )
        raise
