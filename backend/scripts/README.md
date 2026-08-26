# Backend Scripts

This directory contains utility scripts for the Legal Case Search backend.

## Available Scripts

### init_documents.py
Initializes the PostgreSQL document database by processing all `.docx` files from the `cases/` folder.

**What it does:**
- Finds all `.docx` files in the project's `cases/` folder
- Extracts text content from each document
- Splits content into overlapping chunks (configurable via settings)
- Enables `pgvector` and creates `documents` / `document_chunks` tables
- Generates embeddings for each chunk
- Saves document metadata, full text, chunks, and vector embeddings in PostgreSQL
- Filters out Windows NTFS alternate data streams (`.docxZone.Identifier`, etc.)

**Usage:**
```bash
cd backend
source venv/bin/activate
python scripts/init_documents.py
```

**Output:**
```
Found 2 .docx files
Processing: [2026] NSWCATAD 245.docx
  ✓ Extracted 37 chunks from [2026] NSWCATAD 245.docx
  Content size: 24574 characters
   Generating embeddings for 37 chunks
   Saved 37 embedded chunks to PostgreSQL

Processing: [2026] NSWIC 44.docx
  ✓ Extracted 53 chunks from [2026] NSWIC 44.docx
  Content size: 32710 characters
   Generating embeddings for 53 chunks
   Saved 53 embedded chunks to PostgreSQL
```

**Database Output:**
- `documents` table - document metadata and full extracted text
- `document_chunks` table - chunk text and `vector(384)` embeddings
- `document_chunks_embedding_hnsw_idx` - pgvector HNSW cosine index

**Verify Output:**
```bash
python scripts/verify_embeddings.py
```

**Configuration:**
Edit `app/config.py` to adjust:
- `CHUNK_SIZE`: Tokens per chunk (default: 512)
- `CHUNK_OVERLAP`: Token overlap between chunks (default: 100)
- `EMBEDDING_PROVIDER`: `hashing` for local fallback, or `sentence-transformers` for local/downloaded transformer models
- `EMBEDDING_DIMENSION`: Vector size stored in PostgreSQL (default: 384)

### append_documents.py
Adds new documents to PostgreSQL without reprocessing documents already stored in the database.

**What it does:**
- Reads existing document filenames from PostgreSQL
- Finds all `.docx` files in the `cases/` folder
- **Skips documents already stored** (by filename)
- Processes only **new documents** not in PostgreSQL
- Generates embeddings for new document chunks
- Saves metadata, chunks, and embeddings to PostgreSQL

**Usage (after initial load):**
```bash
# First time - processes all documents
python scripts/init_documents.py

# Add more .docx files to cases/ folder, then run:
python scripts/append_documents.py
```

**Output when running second time:**
```
PostgreSQL already contains 2 document(s)
Found 2 total .docx files
No new documents found. PostgreSQL is up to date.
Already processed: 2 files
```

**Output when new documents are added:**
```
PostgreSQL already contains 2 document(s)
Found 3 total .docx files
Found 1 new document(s) to process

Processing: [2026] NEW CASE.docx
  ✓ Extracted 42 chunks
   Saved 42 embedded chunks to PostgreSQL

APPEND SUMMARY
New files processed: 1
Successful: 1 ✓
Failed: 0 ✗
Total in PostgreSQL: 3 files
```

**Database Tracking:**
The script checks the `documents` table and skips filenames already stored in PostgreSQL.

**Resetting the Database Load:**
If you want to reprocess all documents:
```bash
PGPASSWORD=aipassword psql -h localhost -U aiuser -d ai -c "truncate document_chunks, documents;"
python scripts/init_documents.py
```

## Processing Pipeline

**Initial Load:**
```
cases/
  ├── [2026] NSWCATAD 245.docx
  └── [2026] NSWIC 44.docx
           ↓
    [init_documents.py]  (processes all files)
           ↓
PostgreSQL
   ├── pgvector extension
   ├── documents (2 rows)
   └── document_chunks (90 rows with vector embeddings)
```

**Incremental Load (add new documents):**
```
Add new .docx files to cases/
           ↓
    [append_documents.py]  (processes only new files)
           ↓
Checks documents table → finds new files → generates embeddings
           ↓
PostgreSQL
   ├── documents (updated with new files)
   └── document_chunks (updated with new embedded chunks)
```

## Next Steps

1. **Run the initialization script (first time only):**
   ```bash
   python scripts/init_documents.py
   ```

2. **For new documents, use append script:**
   ```bash
   # Add more .docx files to cases/ folder, then run:
   python scripts/append_documents.py
   ```

3. **Verify output:**
   ```bash
   python scripts/verify_embeddings.py
   ```

4. **Start the backend:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

5. **Test via API:**
   - Visit http://localhost:8000/docs
   - Try searching with `/api/search` endpoint

## Database Storage

The scripts now store directly in PostgreSQL:

- `documents`: one row per source file, including extracted full text
- `document_chunks`: one row per chunk, including `vector(384)` embeddings
- `document_chunks_embedding_hnsw_idx`: HNSW cosine index for vector search

Run this to verify the current database state:

```bash
python scripts/verify_embeddings.py
```

## Troubleshooting

### "Cases directory not found"
- Ensure you run the script from the `backend/` directory
- Check that `cases/` folder exists at project root level

### "No .docx files found"
- Check file extensions are `.docx` (not `.doc`)
- Ensure files are in `cases/` folder at project root
- Script ignores Windows ADS files automatically (`.docxZone.Identifier`)

### "No content extracted"
- Document may be corrupted or have no readable text
- Check that .docx file opens in Microsoft Word
- PDF files not yet supported by this script (use CLI tools to convert)

### Hugging Face model download fails
- `CERTIFICATE_VERIFY_FAILED`: install corporate certificates with `sudo update-ca-certificates` and set `SSL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` in `backend/.env`.
- `403 Forbidden`: the network/proxy is blocking Hugging Face model files. Download the model on an approved network, copy it to `backend/data/models/all-MiniLM-L6-v2`, then set `EMBEDDING_MODEL_PATH=./data/models/all-MiniLM-L6-v2` in `backend/.env`.
- Restart the backend after changing `.env`.

### PostgreSQL verification fails
- Ensure PostgreSQL is running: `docker compose up -d postgres`.
- Check `DATABASE_URL` in `backend/.env`.
- Re-run `python scripts/init_documents.py` to create `pgvector`, `documents`, and `document_chunks`.
- Verify with `python scripts/verify_embeddings.py`.

## Future Enhancements

- [ ] Support for .pdf and .txt files in bulk
- [x] Database integration (PostgreSQL + pgvector)
- [x] Embedding generation with local hashing provider
- [ ] Optional production embedding upgrade with local sentence-transformers model
- [ ] Progress bar for large document sets
- [ ] Duplicate detection
- [ ] Metadata extraction (author, dates, etc.)
- [ ] Full-text search indexing
