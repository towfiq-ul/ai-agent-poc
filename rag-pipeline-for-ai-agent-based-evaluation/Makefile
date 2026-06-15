# =============================================================
# RAG Pipeline — Makefile
# Usage: make <target>
# =============================================================

COMPOSE        = docker-compose -f docker/docker-compose.yml
COMPOSE_OLLAMA = $(COMPOSE) --profile ollama
BACKEND        = $(COMPOSE) exec backend
FRONTEND       = $(COMPOSE) exec frontend

.DEFAULT_GOAL := help

# ── Help ──────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  RAG Pipeline — available commands"
	@echo ""
	@echo "  Setup"
	@echo "    make setup            Copy .env.example → .env (first-time only)"
	@echo ""
	@echo "  Docker — Groq mode (no local GPU needed)"
	@echo "    make up               Build and start backend + frontend"
	@echo "    make down             Stop all services"
	@echo "    make restart          Restart all services"
	@echo "    make build            Force-rebuild images (after code changes)"
	@echo "    make logs             Tail logs from all services"
	@echo "    make logs-backend     Tail backend logs only"
	@echo "    make logs-frontend    Tail frontend logs only"
	@echo "    make ps               Show running containers and health"
	@echo ""
	@echo "  Docker — Ollama mode (fully local LLM)"
	@echo "    make up-ollama        Start backend + frontend + Ollama container"
	@echo "    make pull-model       Pull the model defined in .env into Ollama"
	@echo "    make down-ollama      Stop all services including Ollama"
	@echo ""
	@echo "  RAG operations (requires running stack)"
	@echo "    make index-sample     Index the built-in sample knowledge base"
	@echo "    make reset-db         Drop and recreate the vector database"
	@echo "    make query Q='...'    Run a one-off query via the API"
	@echo "    make status           Show backend status (provider, model, etc.)"
	@echo ""
	@echo "  Local development (no Docker)"
	@echo "    make install          Install all Python deps locally"
	@echo "    make dev-backend      Run FastAPI with hot-reload on :8080"
	@echo "    make dev-frontend     Run Django dev server on :8000"
	@echo ""
	@echo "  Maintenance"
	@echo "    make shell-backend    Open a bash shell in the backend container"
	@echo "    make shell-frontend   Open a bash shell in the frontend container"
	@echo "    make clean            Remove containers and local build cache"
	@echo "    make clean-vols       Remove named volumes (wipes DB + model cache)"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────
.PHONY: setup
setup:
	@if [ ! -f .env ]; then \
	  cp .env.example .env; \
	  echo ""; \
	  echo "  ✅  .env created from .env.example"; \
	  echo "  ✏️   Edit .env and set LLM_PROVIDER + model/key before running 'make up'"; \
	  echo ""; \
	else \
	  echo "ℹ️   .env already exists — skipping. Delete it to reset."; \
	fi

# ── Docker: Groq / default mode ───────────────────────────────
.PHONY: up-d up
up-d:
	$(COMPOSE) up --build -d
	@echo ""
	@echo "  ✅  Stack is up"
	@echo "  🌐  Frontend  →  http://localhost:8000"
	@echo "  🔌  Backend   →  http://localhost:8080"
	@echo "  📖  API docs  →  http://localhost:8080/docs"
	@echo ""
	@echo "  Next: make index-sample"
	@echo ""

up:
	$(COMPOSE) up --build
	@echo ""
	@echo "  ✅  Stack is up"
	@echo "  🌐  Frontend  →  http://localhost:8000"
	@echo "  🔌  Backend   →  http://localhost:8080"
	@echo "  📖  API docs  →  http://localhost:8080/docs"
	@echo ""
	@echo "  Next: make index-sample"
	@echo ""

.PHONY: down stop
down:
	$(COMPOSE) down

stop:
	@test -n "$(SVC)" || (echo "Usage: make stop SVC=api" && exit 1)
	$(COMPOSE) stop $(SVC)

.PHONY: restart
restart:
	$(COMPOSE) restart

.PHONY: build
build:
	$(COMPOSE) build --no-cache

.PHONY: logs
logs:
	$(COMPOSE) logs -f backend frontend ollama

.PHONY: logs-backend
logs-backend:
	$(COMPOSE) logs -f backend

.PHONY: logs-frontend
logs-frontend:
	$(COMPOSE) logs -f frontend

.PHONY: logs-ollama
logs-ollama:
	$(COMPOSE) logs -f ollama

.PHONY: ps
ps:
	$(COMPOSE) ps

.PHONY: reload
reload:
	@test -n "$(SVC)" || (echo "Usage: make reload SVC=api" && exit 1)
	$(COMPOSE) up -d --build --no-deps $(SVC)

# ── Docker: Ollama mode ───────────────────────────────────────
.PHONY: up-ollama-d up-ollama
up-ollama-d:
	$(COMPOSE) up --build --no-deps ollama -d
	@echo ""
	@echo "  ✅  Stack is up (with Ollama)"
	@echo "  🌐  Frontend  →  http://localhost:8000"
	@echo "  🔌  Backend   →  http://localhost:8080"
	@echo "  🤖  Ollama    →  http://localhost:11434"
	@echo ""
	@echo "  Next: make pull-model   (downloads the model into Ollama)"
	@echo ""

up-ollama:
	$(COMPOSE) up --build --no-deps ollama
	@echo ""
	@echo "  ✅  Stack is up (with Ollama)"
	@echo "  🌐  Frontend  →  http://localhost:8000"
	@echo "  🔌  Backend   →  http://localhost:8080"
	@echo "  🤖  Ollama    →  http://localhost:11434"
	@echo ""
	@echo "  Next: make pull-model   (downloads the model into Ollama)"
	@echo ""

.PHONY: pull-model
pull-model:
	@MODEL=$$(grep ^AI_AGENT_MODEL .env | cut -d= -f2 | tr -d ' "'); \
	if [ -z "$$MODEL" ]; then echo "❌ AI_AGENT_MODEL not set in .env"; exit 1; fi; \
	echo "Pulling model: $$MODEL"; \
	$(COMPOSE_OLLAMA) exec ollama ollama pull $$MODEL

.PHONY: down-ollama
down-ollama:
	$(COMPOSE_OLLAMA) down

# ── RAG operations ────────────────────────────────────────────
.PHONY: index-sample
index-sample:
	@echo "Indexing sample knowledge base…"
	@curl -s -X POST http://localhost:8080/index/sample | python3 -m json.tool

.PHONY: reset-db
reset-db:
	@echo "Resetting vector database…"
	@curl -s -X POST http://localhost:8080/reset | python3 -m json.tool

.PHONY: status
status:
	@curl -s http://localhost:8080/status | python3 -m json.tool

.PHONY: query
query:
	@if [ -z "$(Q)" ]; then \
	  echo "Usage: make query Q='your question here'"; exit 1; \
	fi
	@python3 -c "import json,sys; print(json.dumps({'query': sys.argv[1], 'top_k': 5}))" "$(Q)" | \
	  curl -s -X POST http://localhost:8080/query \
	    -H "Content-Type: application/json" \
	    -d @- | python3 -m json.tool

# ── Local development ─────────────────────────────────────────
.PHONY: install
install:
	.venv/bin/pip install -r backend/requirements.txt
	.venv/bin/pip install -r frontend/requirements.txt

.PHONY: dev-backend
dev-backend:
	@echo "Starting FastAPI dev server on :8080 …"
	cd backend/src && ../../.venv/bin/uvicorn api:app --host 0.0.0.0 --port 8080 --reload

.PHONY: dev-frontend
dev-frontend:
	@echo "Starting Django dev server on :8000 …"
	cd frontend && watchmedo auto-restart --directory=./ --pattern="*.py" --recursive -- /bin/bash -c "DJANGO_DEBUG=true ../.venv/bin/python manage.py runserver 0.0.0.0:8000"

# ── Maintenance ───────────────────────────────────────────────
.PHONY: shell-backend
shell-backend:
	$(BACKEND) /bin/bash

.PHONY: shell-frontend
shell-frontend:
	$(FRONTEND) /bin/bash

.PHONY: clean
clean:
	$(COMPOSE_OLLAMA) down --rmi local --remove-orphans
	docker builder prune -f
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅  Cleaned containers and build cache."

.PHONY: clean-vols
clean-vols:
	@echo "⚠️  This will delete the vector database AND all downloaded model caches."
	@read -p "Are you sure? [y/N] " ans && [ "$$ans" = "y" ] || exit 0
	$(COMPOSE_OLLAMA) down -v
	@echo "✅  Volumes removed."
