#!/usr/bin/env python3
"""Download the configured embedding model for offline/local use."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Download the embedding model and save it under data/models."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SystemExit(
            "sentence-transformers is required. Install it with: "
            "pip install sentence-transformers torch --prefer-binary"
        ) from exc

    model_name = settings.embedding_model
    output_dir = Path("data/models/all-MiniLM-L6-v2")

    logger.info("Downloading embedding model: %s", model_name)
    logger.info("Using CA bundle: %s", settings.ssl_ca_bundle or "Python default")
    logger.info("Saving model to: %s", output_dir)

    try:
        model = SentenceTransformer(model_name)
        output_dir.mkdir(parents=True, exist_ok=True)
        model.save(str(output_dir))
    except Exception as exc:
        raise SystemExit(
            "Failed to download the embedding model. If this shows HTTP 403, "
            "your network is blocking Hugging Face. Download the model on an "
            "approved network and copy the folder to backend/data/models/all-MiniLM-L6-v2. "
            "Then set EMBEDDING_MODEL_PATH=./data/models/all-MiniLM-L6-v2 in backend/.env."
        ) from exc

    logger.info("Embedding model saved successfully")
    logger.info("Add this to backend/.env if not already set:")
    logger.info("EMBEDDING_MODEL_PATH=./data/models/all-MiniLM-L6-v2")


if __name__ == "__main__":
    main()