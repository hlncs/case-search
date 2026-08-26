# Legal Case Search - Setup & Testing Guide

## ✅ Installation Status

### Backend
- ✅ Python virtual environment created: `backend/venv`
- ✅ Core dependencies installed (49 packages)
- ✅ Configuration file created: `backend/.env`
- ✅ Backend imports verified - no errors
- ✅ Backend startup tested - runs successfully
- ✅ Ollama service detected and ready

### Frontend  
- ✅ Node.js dependencies installed (283 packages)
- ✅ Configuration file created: `frontend/.env`
- ✅ TypeScript compilation successful - no errors
- ✅ All type imports configured correctly

### Scripts & Tools
- ✅ `backend/scripts/init_documents.py` - Initial document indexing
- ✅ `backend/scripts/append_documents.py` - Incremental document loading
- ✅ PostgreSQL document tracking - Automatic duplicate prevention by filename
- ✅ `backend/scripts/verify_embeddings.py` - PostgreSQL embedding verification

### AI/ML Features (INSTALLED)
- ✅ **sentence-transformers** 5.7.0 - Document embeddings
- ✅ **PyTorch** 2.13.0+cu130 - Deep learning framework
- ✅ **ollama** 0.6.2 - LLM client
- ✅ **langchain** 1.3.15 - RAG framework
- ✅ **langchain-community** 0.4.2 - Community integrations
- ✅ **local hashing embeddings** - Active fallback when Hugging Face is blocked
- Ready for: Standard vector search, RAG retrieval/fallback answers, Agent retrieval workflow

## Quick Start

### Backend Setup

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate

# Start the backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Started server process
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Backend will be available at:** http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend  
cd frontend

# Install dependencies (if not done)
npm install

# Start development server
npm run dev

# Server will open automatically at http://localhost:5173
```

**Frontend will be available at:** http://localhost:5173

## Document Loading

Before starting the backend, initialize your document index to make legal cases searchable.
The active storage path is PostgreSQL, not JSON files.

### Initial Document Load

```bash
# From backend directory (with venv activated)
python scripts/init_documents.py

# Expected output:
# Found 2 .docx files
# Processing: [2026] NSWCATAD 245.docx
#   ✓ Extracted 37 chunks
# Processing: [2026] NSWIC 44.docx
#   ✓ Extracted 53 chunks
# 
# INIT SUMMARY
# Total files processed: 2
# Successful: 2 ✓
# Failed: 0 ✗
```

**Output:** Creates PostgreSQL tables, enables `pgvector`, and stores documents, chunks, and embeddings in PostgreSQL.

**Verify database embeddings:**
```bash
python scripts/verify_embeddings.py

# Expected output includes:
# pgvector extension: installed
# public.document_chunks: 90 rows
# public.documents: 2 rows
# public.document_chunks.embedding: 90/90 populated
# Embeddings populated: YES
```

### Adding New Documents (Incremental Load)

When you add new `.docx` files to the `cases/` folder:

```bash
# Run the append script (same directory structure)
python scripts/append_documents.py

# This script:
# ✅ Checks which filenames already exist in PostgreSQL
# ✅ Processes only NEW documents
# ✅ Generates embeddings for new chunks
# ✅ Stores documents, chunks, and vectors in PostgreSQL
# ✅ Skips existing files (no duplicates)
```

**Example workflow:**
1. Add new legal documents to `cases/` folder
2. Run `python scripts/append_documents.py`
3. New documents are indexed without reprocessing old ones

### Documentation

For detailed configuration and troubleshooting, see [backend/scripts/README.md](backend/scripts/README.md):
- Chunk size and overlap configuration
- PostgreSQL reset procedures
- Embedding verification
- Support for additional file formats

## Environment Configuration

### Backend (.env)
Located at `backend/.env`:
- **DATABASE_URL**: PostgreSQL connection string
- **OLLAMA_BASE_URL**: LLM service endpoint (http://localhost:11434)
- **OLLAMA_MODEL**: llama3.2:3b
- **OLLAMA_TIMEOUT**: 10 seconds, keeps backend responses below frontend timeout
- **OLLAMA_NUM_PREDICT**: 256 tokens, caps local CPU generation length
- **EMBEDDING_PROVIDER**: `hashing` for local embeddings without Hugging Face download
- **EMBEDDING_MODEL_NAME**: sentence-transformers/all-MiniLM-L6-v2
- **SSL_CA_BUNDLE**: `/etc/ssl/certs/ca-certificates.crt` for corporate/Zscaler TLS inspection
- **EMBEDDING_MODEL_PATH**: Optional local model path when Hugging Face is blocked
- **UPLOAD_DIR**: Document storage directory
- **CHUNK_SIZE**: 512 tokens per chunk
- **CHUNK_OVERLAP**: 100 tokens
- **RAG_MAX_CHUNKS**: 5 context chunks
- **CORS_ORIGINS**: Allows localhost:5173 and localhost:3000

### Frontend (.env)
Located at `frontend/.env`:
- **VITE_API_BASE_URL**: http://localhost:8000
- **VITE_DEBUG**: false

## API Endpoints

### Search Endpoints
- `POST /api/search` - Vector similarity search
- `POST /api/rag-query` - RAG-powered search with citations
- `POST /api/agent-query` - Autonomous agent with reasoning

### Case Endpoints
- `GET /api/cases/{caseId}` - Get case details
- `GET /api/cases?limit=10&offset=0` - List cases with pagination

### Document Endpoints
- `POST /api/documents/upload` - Upload a document
- `GET /api/documents` - List uploaded documents
- `DELETE /api/documents/{docId}` - Delete document

### API Documentation
Interactive API docs available at: http://localhost:8000/docs

## Verification Checklist

### Backend Verification
```bash
cd backend
source venv/bin/activate

# 1. Check Python imports
python -m py_compile app/main.py
# Expected: No output (success)

# 2. List installed packages
pip list | grep -E 'fastapi|psycopg2|pandas|sqlalchemy'
# Expected: All core packages listed

# 3. Start server with timeout
timeout 10 python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# Expected: Server starts and runs without errors
```

### Frontend Verification
```bash
cd frontend

# 1. Check TypeScript compilation
npm run type-check
# Expected: No errors found

# 2. Run linting
npm run lint
# Expected: No major warnings

# 3. Build production bundle
npm run build
# Expected: dist/ folder created with bundled files
```

## AI/ML Features (INSTALLED ✅)

**Status:** All packages successfully installed and verified!

Installed packages provide:
- **Embeddings**: Local hashing embeddings by default; sentence-transformers available when a local model path is configured
- **LLM Integration**: Direct connection to Ollama models with timeout and output caps
- **RAG Framework**: Retrieval-augmented generation with langchain
- **Advanced Reasoning**: Agent-based query processing with retrieval fallback

**Verification:**
```bash
cd backend
source venv/bin/activate

# Verify packages
python -c "import sentence_transformers, torch; print('✓ Ready')"

# Verify PostgreSQL embeddings
python scripts/verify_embeddings.py
```

### Corporate Certificate / Zscaler Setup

If model loading fails with `CERTIFICATE_VERIFY_FAILED`, make sure the Zscaler certificates are installed in WSL:

```bash
ls -l /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

The backend is configured to use the WSL CA bundle:

```bash
SSL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

At startup, the backend maps this to `REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE`, and `CURL_CA_BUNDLE` so Hugging Face, requests, and related Python libraries use the trusted corporate CA bundle.

### Ollama Docker Certificate Setup

The `ollama` Docker container also needs the corporate CA bundle when pulling models from `registry.ollama.ai`. `docker-compose.yaml` mounts the WSL CA bundle into the container and sets:

```yaml
SSL_CERT_FILE: /etc/ssl/certs/ca-certificates.crt
SSL_CERT_DIR: /etc/ssl/certs
```

After adding or updating certificates in WSL, recreate the Ollama container so it receives the mounted CA bundle:

```bash
cd ~/Projects/Demos/case-search
sudo update-ca-certificates
docker compose up -d --force-recreate ollama
```

Verify the container can see the CA bundle:

```bash
docker compose exec ollama sh -lc 'echo $SSL_CERT_FILE && ls -l $SSL_CERT_FILE'
```

Then pull the configured CPU-friendly model inside the container:

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

If Docker reports `permission denied while trying to connect to the Docker daemon socket`, run the Docker commands with `sudo`, or add your WSL user to the `docker` group and reopen the shell.

### If Hugging Face Returns 403 Forbidden

A `403 Forbidden` response means TLS is working, but the corporate network/proxy is blocking access to Hugging Face model files. Use a local model directory instead:

```bash
cd backend
source venv/bin/activate

# Try this first if Hugging Face is allowed from your network
python scripts/download_embedding_model.py
```

If that script also returns `403`, download `sentence-transformers/all-MiniLM-L6-v2` from an approved network, copy the complete model folder to:

```text
backend/data/models/all-MiniLM-L6-v2
```

Then add this to `backend/.env`:

```bash
EMBEDDING_MODEL_PATH=./data/models/all-MiniLM-L6-v2
```

Restart the backend after changing `.env`.

**Note:** To reinstall or update these packages:
```bash
pip install --upgrade sentence-transformers torch ollama langchain langchain-community --prefer-binary
```

## Project Structure

```
case-search/
├── backend/
│   ├── venv/                    # Python virtual environment
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Configuration settings
│   │   ├── models/             # Data models
│   │   ├── services/           # Business logic
│   │   ├── routes/             # API endpoints
│   │   └── utils/              # Utilities
│   ├── .env                    # Environment variables
│   ├── requirements.txt        # Python dependencies
│   └── requirements-ai.txt     # Optional AI dependencies
│
├── frontend/
│   ├── node_modules/           # Node dependencies
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API client
│   │   ├── models/            # TypeScript interfaces
│   │   ├── utils/             # Utilities
│   │   ├── App.tsx            # Main app
│   │   └── main.tsx           # Entry point
│   ├── .env                   # Environment variables
│   ├── vite.config.ts        # Vite configuration
│   ├── tsconfig.json         # TypeScript config
│   └── package.json          # Dependencies
│
├── docker-compose.yaml        # Database & services setup
└── README.md
```

## Database Setup

The system uses PostgreSQL with pgvector. The document initialization script creates the required extension and tables automatically:

```bash
# Start PostgreSQL via docker-compose
docker-compose up -d

# Initialize documents, chunks, and embeddings
cd backend
source venv/bin/activate
python scripts/init_documents.py

# Verify embeddings
python scripts/verify_embeddings.py
```

## Troubleshooting

### Backend Won't Start
- Check `.env` file exists in backend/
- Verify venv is activated: `source venv/bin/activate`
- Check if port 8000 is available: `lsof -i :8000`

### Frontend Build Fails
- Delete `node_modules` and `package-lock.json`, then `npm install`
- Clear `.vite` cache
- Check TypeScript: `npm run type-check`

### CORS Issues
- Verify frontend URL in backend `.env` CORS_ORIGINS
- Frontend should be `http://localhost:5173`
- Backend should be `http://localhost:8000`

### API Connection Issues
- Check backend is running: `http://localhost:8000/docs`
- Verify `VITE_API_BASE_URL` in frontend `.env`
- Check browser console for network errors

### Hugging Face Certificate or 403 Errors
- `CERTIFICATE_VERIFY_FAILED`: confirm `SSL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` is in `backend/.env` and run `sudo update-ca-certificates` in WSL.
- `403 Forbidden`: the certificate is trusted, but the network/proxy is blocking Hugging Face. Use `EMBEDDING_MODEL_PATH=./data/models/all-MiniLM-L6-v2` after copying the model locally.
- After changing `.env`, restart the backend server.

### Ollama Pull Certificate Errors
- Recreate the Ollama container after updating WSL certificates: `docker compose up -d --force-recreate ollama`.
- Confirm the container has `SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt`.
- Pull with: `docker compose exec ollama ollama pull llama3.2:3b`.
- Use `sudo docker compose ...` if your WSL user cannot access `/var/run/docker.sock`.

### RAG Timeout on CPU
- The backend uses `OLLAMA_TIMEOUT=10` and `OLLAMA_NUM_PREDICT=256` to stay below the frontend 30s timeout.
- If Ollama is too slow, RAG returns a retrieval-based answer from PostgreSQL sources instead of failing.
- For faster local inference, use `llama3.2:1b` and update `OLLAMA_MODEL` in `backend/.env`.

## Next Steps

### 1. Initialize Documents (Required)
```bash
cd backend
source venv/bin/activate
python scripts/init_documents.py
```
This creates PostgreSQL tables, enables pgvector, and stores document embeddings.

### 2. Start the Application
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Search**: Search for legal cases from loaded documents

### 4. Manage Documents
- **Add new documents**: Copy `.docx` files to `cases/` folder
- **Index new files**: Run `python scripts/append_documents.py`
- **See full guide**: [backend/scripts/README.md](backend/scripts/README.md)

### 5. Verify Database Embeddings
```bash
cd backend
source venv/bin/activate
python scripts/verify_embeddings.py
```
Expected current state: 2 documents and 90/90 populated chunk embeddings.

### 6. AI/ML Features (Installed ✅)
Advanced RAG and agent capabilities are ready to use:
- **Standard search**: Vector similarity using embeddings
- **RAG mode**: LLM-powered answers with source citations
- **Agent mode**: Autonomous reasoning and multi-step queries

No additional setup needed for retrieval-backed answers. Full LLM generation depends on an installed and responsive local Ollama model.

### 7. Deploy to Production
- Build frontend: `npm run build`
- Configure HTTPS/SSL
- Set up reverse proxy (nginx/Caddy)
- Deploy containers to your infrastructure

## Support & Documentation

- Backend API docs: http://localhost:8000/docs
- Vite docs: https://vitejs.dev
- React docs: https://react.dev
- FastAPI docs: https://fastapi.tiangolo.com
- Material-UI docs: https://mui.com

## Version Information

- **Python**: 3.14 (with compatibility fixes)
- **Node.js**: 18+ required
- **FastAPI**: 0.104.1
- **React**: 18.2.0
- **TypeScript**: 5.2.2
- **PostgreSQL**: 15+ with pgvector
- **Ollama**: llama3.2:3b configured for local CPU inference
- **Ollama**: Latest (for LLM inference)
