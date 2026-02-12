# DevForge

DevForge is a production-grade, AI-powered developer portfolio generator.  
It ingests GitHub activity, analyzes projects and commits with distributed workers, and generates polished portfolio sites with realtime progress updates.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Flower: `http://localhost:5555`

## Repository Layout

- `backend/`: FastAPI, SQLAlchemy, Celery, Redis integration
- `frontend/`: Next.js 14 app router client
- `docs/`: architecture and deployment docs

## Development Status

This scaffold includes:

- Dockerized local stack (Postgres, Redis, API, worker, beat, Flower, frontend)
- Async FastAPI backend with JWT auth + GitHub OAuth flow
- Portfolio CRUD + generation jobs
- Celery task orchestration with progress events
- Redis rate limiting and multi-layer cache utilities
- Next.js dashboard/editor/generation progress views

## Commands

```bash
# Backend tests
docker compose exec api pytest -q

# Lint backend
docker compose exec api ruff check .

# Generate migration (inside backend container)
docker compose exec api alembic revision --autogenerate -m "message"
```
