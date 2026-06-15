# RAG Pipeline for AI Agent Based Evaluation

A production-ready Retrieval-Augmented Generation (RAG) system built entirely on
free and open-source tooling. No OpenAI key required.

```
┌─────────────────────────────────────────────────────────┐
│  Browser  →  Django :8000  →  FastAPI :8080  →  LLM     │
│                                     ↕                   │
│                               LanceDB (vector DB)       │
│                               sentence-transformers     │
└─────────────────────────────────────────────────────────┘
```

## Tech stack

| Layer       | Tool                      | Notes                                   |
|-------------|---------------------------|-----------------------------------------|
| Frontend    | Django 5 + WhiteNoise     | Proxy layer, HTML UI                    |
| Backend     | FastAPI + Uvicorn         | REST API, RAG pipeline                  |
| Embeddings  | sentence-transformers     | Local, no API key -> 'all-MiniLM-L6-v2' |
| Vector DB   | LanceDB + PyArrow         | File-based, no server needed            |
| LLM (local) | Ollama                    | Runs on your machine / GPU              |
| LLM (cloud) | Groq API                  | Free tier, very fast                    |
| Infra       | Docker Compose + Makefile | One-command deployment                  |

## Project structure

```
rag-pipeline-for-ai-agent-based-evaluation/
│
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── Makefile
├── README.md
│
├── sample_data/                          ← (samples)
│   ├── source/
│   │   ├── ml_fundamentals.md
│   │   ├── prompt_engineering.md
│   │   ├── rag_and_embeddings.md
│   │   └── transformers_and_llms.md
│   └── eval/
│       └── sample_questions.json
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── api.py                        ← FastAPI app, all REST endpoints
│       ├── rag_pipeline.py               ← pipeline orchestrator
│       ├── impl/
│       │   ├── __init__.py
│       │   ├── datastore.py              ← LanceDB + sentence-transformers
│       │   ├── evaluator.py              ← LLM-based Q&A scorer
│       │   ├── indexer.py                ← chunker
│       │   ├── response_generator.py     ← LLM answer generation
│       │   └── retriever.py              ← vector similarity search
│       ├── interface/
│       │   ├── __init__.py
│       │   ├── base_datastore.py
│       │   ├── base_evaluator.py
│       │   ├── base_indexer.py
│       │   ├── base_response_generator.py
│       │   └── base_retriever.py
│       └── util/
│           ├── __init__.py
│           ├── extract_xml.py
│           └── invoke_ai.py              ← Ollama / Groq router
│
└── frontend/
    ├── Dockerfile
    ├── requirements.txt
    ├── manage.py
    ├── rag_ui_project/                   ← Django project
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── rag_ui/                           ← Django app
        ├── __init__.py
        ├── apps.py
        ├── urls.py
        ├── views.py                      ← proxy views → FastAPI
        ├── templates/
        │   └── rag_ui/
        │       ├── base.html
        │       ├── index.html            ← chat page
        │       └── evaluate.html         ← evaluation page
        └── static/
            └── rag_ui/
                ├── css/
                │   └── main.css
                └── js/
                    ├── chat.js
                    ├── evaluate.js
                    └── status.js
```

## Quickstart

### With Groq (no GPU, fastest setup)

```bash
make setup
# Edit .env:
#   LLM_PROVIDER=groq
#   AI_AGENT_MODEL=llama-3.1-8b-instant
#   GROQ_API_KEY=<your key from console.groq.com>
make up
make index-sample
# Open http://localhost:8000
```

### With Ollama (fully local, no API key)

```bash
make setup
# Edit .env — defaults are already set for Ollama
make up-ollama
make pull-model       # downloads llama3.2 into the Ollama container
make index-sample
# Open http://localhost:8000
```

## All commands

```bash
make help             # show all available commands

make up               # start (Groq mode)
make up-ollama        # start with local Ollama
make down             # stop
make build            # force rebuild after code changes
make logs             # tail all logs
make logs-backend     # tail backend only
make logs-frontend    # tail frontend only
make ps               # container status + health

make index-sample     # index sample knowledge base
make reset-db         # wipe vector database
make status           # show backend config
make query Q="..."    # one-off query from terminal

make dev-backend      # FastAPI hot-reload on :8080
make dev-frontend     # Django dev server on :8000
make install          # install deps locally

make shell-backend    # bash inside backend container
make shell-frontend   # bash inside frontend container
make clean            # remove containers + build cache
make clean-vols       # remove volumes (wipes DB + model cache)
```

## API endpoints

The FastAPI backend exposes these endpoints (also browseable at `http://localhost:8080/docs`):

| Method | Path          | Description                           |
|--------|---------------|---------------------------------------|
| GET    | /health       | Liveness check                        |
| GET    | /status       | Provider, model, embedding info       |
| POST   | /query        | Ask a question, get a grounded answer |
| POST   | /index/files  | Upload and index .md / .txt files     |
| POST   | /index/sample | Index the built-in sample data        |
| POST   | /reset        | Wipe and recreate the vector table    |
| POST   | /evaluate     | Run Q&A evaluation suite              |

## Environment variables

| Variable               | Default               | Description                      |
|------------------------|-----------------------|----------------------------------|
| `LLM_PROVIDER`         | `ollama`              | `ollama` or `groq`               |
| `AI_AGENT_MODEL`       | `llama3.2`            | Model name for the LLM           |
| `OLLAMA_BASE_URL`      | `http://ollama:11434` | Ollama server URL                |
| `GROQ_API_KEY`         | —                     | Required when LLM_PROVIDER=groq  |
| `LLM_TIMEOUT_SECONDS`  | `180`                 | Request timeout for LLM calls    |
| `EMBEDDING_MODEL`      | `all-MiniLM-L6-v2`    | sentence-transformers model name |
| `LANCEDB_PATH`         | `/data/lancedb`       | Path for vector DB files         |
| `DJANGO_SECRET_KEY`    | —                     | Required in production           |
| `DJANGO_DEBUG`         | `false`               | Set `true` for dev               |
| `DJANGO_ALLOWED_HOSTS` | `localhost ...`       | Space-separated allowed hosts    |

## Adding your own documents

Drop `.md` or `.txt` files into `sample_data/source/` and run:

```bash
make index-sample
```

Or upload files directly through the UI on the Chat page.

---

Built by [Towfiqul Islam](https://towfiq-ul.github.io)
