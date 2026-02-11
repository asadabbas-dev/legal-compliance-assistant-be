# Legal & Compliance Knowledge Assistant — Backend

Production-focused FastAPI backend for a **personal** legal/compliance RAG assistant.

## Tech Stack

- FastAPI
- Python 3.10+
- PostgreSQL + pgvector
- SQLAlchemy 2
- OpenAI or Anthropic
- Local filesystem storage (`UPLOAD_DIR`)

## Prerequisites

- Python 3.10+
- PostgreSQL running locally
- pgvector installed in your PostgreSQL instance

## Run Locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

## Environment Variables

Copy and edit `.env`:

```bash
cp .env.example .env
```

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`
- `UPLOAD_DIR`
- `LLM_PROVIDER`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `EMBEDDING_MODEL`
- `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`
- `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`, `MAX_CHAT_MEMORY_MESSAGES`

## API Overview (v1)

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Auth is optional for core usage:
- Guest users can upload and chat without login.
- Guest chat history is not persisted.
- Logged-in users get persistent chat history.

### Documents
- `POST /api/v1/documents/upload`
- `POST /api/v1/documents/process`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{id}`

### Chat + RAG
- `POST /api/v1/chat/create`
- `GET /api/v1/chat`
- `GET /api/v1/chat/{id}`
- `POST /api/v1/chat/{id}/message`
- `GET /api/v1/chat/{id}/history`
- `POST /api/v1/rag/query`

### Feedback
- `POST /api/v1/feedback`

## pgvector Setup

If startup logs `extension "vector" is not available`, install pgvector for your PostgreSQL:

### Homebrew PostgreSQL
```bash
brew install pgvector
```

### EnterpriseDB PostgreSQL (macOS example)
```bash
cd /tmp
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
export PG_CONFIG=/Library/PostgreSQL/15/bin/pg_config
make
sudo make install
```

Then restart PostgreSQL and run:

```sql
CREATE EXTENSION vector;
```
