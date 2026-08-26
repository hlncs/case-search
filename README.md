# Legal Case Search

A local legal case search application with a React frontend, FastAPI backend, PostgreSQL/pgvector semantic search, RAG-style answers, and an agent-style retrieval workflow.

## Current Status

- Frontend: React + TypeScript + Vite + Material UI
- Backend: FastAPI + PostgreSQL + pgvector
- Documents: `.docx` files from `cases/` are parsed, chunked, embedded, and stored in PostgreSQL
- Embeddings: `EMBEDDING_PROVIDER=hashing` is active, so ingestion/search works without downloading Hugging Face models
- Database: verified with 2 documents and 90 populated chunk embeddings
- RAG/Agent: return PostgreSQL-backed retrieval results and use Ollama when the configured local model responds in time
- Ollama: configured for `llama3.2:3b` with CPU-friendly timeout/output limits

## Quick Start

Start infrastructure:

```bash
docker compose up -d
```

Initialize or refresh document embeddings:

```bash
cd backend
source venv/bin/activate
python scripts/init_documents.py
python scripts/verify_embeddings.py
```

Start backend:

```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Start frontend:

```bash
cd frontend
npm run dev
```

Open the app at http://localhost:5173 and the API docs at http://localhost:8000/docs.

## Document Loading

Initial load:

```bash
cd backend
source venv/bin/activate
python scripts/init_documents.py
```

Append only new `.docx` files added to `cases/`:

```bash
python scripts/append_documents.py
```

Verify PostgreSQL embeddings:

```bash
python scripts/verify_embeddings.py
```

Expected current output includes:

```text
pgvector extension: installed
public.documents: 2 rows
public.document_chunks: 90 rows
public.document_chunks.embedding: 90/90 populated
Embeddings populated: YES
```

## Configuration Notes

Backend settings live in `backend/.env`.

Important current values:

```bash
DATABASE_URL=postgresql://aiuser:aipassword@localhost:5432/ai
EMBEDDING_PROVIDER=hashing
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
SSL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=10
OLLAMA_NUM_PREDICT=256
```

Use `EMBEDDING_MODEL_PATH=./data/models/all-MiniLM-L6-v2` if you later copy a sentence-transformers model locally and want transformer embeddings instead of hashing embeddings.

## Corporate Certificates

WSL and Docker need the corporate/Zscaler CA bundle for HTTPS model downloads.

```bash
sudo update-ca-certificates
```

The backend uses:

```bash
SSL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

The `ollama` service in `docker-compose.yaml` mounts the same CA bundle into the container and sets `SSL_CERT_FILE` / `SSL_CERT_DIR`.

To recreate Ollama after certificate changes:

```bash
docker compose up -d --force-recreate ollama
docker compose exec ollama ollama pull llama3.2:3b
```

Use `sudo docker compose ...` if your WSL user cannot access the Docker daemon socket.

## Search Modes

- Standard: direct pgvector similarity search over `document_chunks.embedding`
- RAG: retrieves relevant chunks, then uses Ollama when available; falls back to grounded retrieved excerpts if Ollama is slow or unavailable
- Agent: uses search tools and returns sources/reasoning trace; avoids long loops when Ollama is unavailable

See `SETUP_GUIDE.md` for the full setup and troubleshooting guide.
