# Legal & Compliance Knowledge Assistant — Backend

FastAPI backend for the Legal & Compliance Knowledge Assistant. Handles PDF upload, chunking, embeddings, vector search, and LLM-based Q&A with citations.

## Tech Stack

- **FastAPI**
- **Python 3.10+**
- **PostgreSQL** + **pgvector** (vector extension)
- **SQLAlchemy 2**
- **OpenAI** or **Anthropic** (configurable LLM provider)

## Prerequisites

- **Python 3.10+**
- **PostgreSQL** with pgvector (or use Docker Compose from repo root)

## Project Structure

```
app/
  main.py              # FastAPI app, lifespan, CORS, router
  core/
    config.py          # Settings from environment
    database.py        # Engine, session, Base
  api/
    deps.py            # get_db dependency
    v1/
      router.py        # Aggregates v1 endpoints
      endpoints/       # Upload, documents, ask, feedback
  schemas/             # Pydantic request/response models
  models/              # SQLAlchemy ORM (Document, Chunk, Feedback)
  services/            # Business logic
    document_service.py
    ingestion_service.py   # PDF → chunks + embeddings
    embedding_service.py
    llm_service.py         # Provider routing (OpenAI/Anthropic)
    llm_openai.py
    llm_anthropic.py
    llm_prompts.py
    pdf_service.py
requirements.txt
```

## Environment Variables

Copy the example file and set your values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| **Database** | |
| `DB_HOST` | PostgreSQL host (default: `localhost`) |
| `DB_PORT` | Port (default: `5432`) |
| `DB_NAME` | Database name (default: `rag_db`) |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| **Storage** | |
| `UPLOAD_DIR` | Directory for uploaded PDFs (default: `uploads`) |
| **LLM** | |
| `LLM_PROVIDER` | `openai` or `anthropic` |
| `OPENAI_API_KEY` | Required when `LLM_PROVIDER=openai` |
| `OPENAI_MODEL` | e.g. `gpt-4o-mini` |
| `EMBEDDING_MODEL` | e.g. `text-embedding-3-small` |
| `ANTHROPIC_API_KEY` | Required when `LLM_PROVIDER=anthropic` |
| `ANTHROPIC_MODEL` | e.g. `claude-3-5-sonnet-20241022` |
| **RAG** | |
| `CHUNK_SIZE` | Chunk size in characters (default: `1000`) |
| `CHUNK_OVERLAP` | Overlap between chunks (default: `200`) |
| `TOP_K` | Number of chunks retrieved per query (default: `5`) |

## Running Locally

1. Create and activate a virtual environment (recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:

   ```bash
   cp .env.example .env
   # Edit .env: set DB_* and OPENAI_API_KEY (or ANTHROPIC_*)
   ```

4. Ensure PostgreSQL is running and the database exists (e.g. `rag_db`). The app will create the pgvector extension and tables on startup.

5. Start the server:

   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

   Or use the included script:

   ```bash
   ./run.sh
   ```

- **API base:** http://localhost:8000  
- **API v1:** http://localhost:8000/api/v1  
- **Docs:** http://localhost:8000/docs  
- **Health:** http://localhost:8000/health  

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/upload` | Upload a PDF (multipart) |
| GET | `/api/v1/documents` | List uploaded documents |
| POST | `/api/v1/ask` | Ask a question (JSON: `question`), returns answer + citations |
| POST | `/api/v1/feedback` | Submit feedback (helpful / not helpful) |

All responses are JSON. See http://localhost:8000/docs for full request/response schemas.

## Docker

From the repo root, use Docker Compose to run PostgreSQL + backend (see root `README.md`). To build and run only the backend image:

```bash
docker build -t compliance-backend .
docker run -p 8000:8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e OPENAI_API_KEY=sk-... \
  compliance-backend
```

Adjust `DB_HOST` if the database runs in another container or on the host.

## Database

- Uses **pgvector** for storing and querying embeddings (cosine distance).
- Startup creates the `vector` extension and all tables if they do not exist.
- If the database is unavailable at startup, the app still runs; upload and ask endpoints will fail until the DB is reachable.

## License

Same as the parent project.
