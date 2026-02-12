# Development Setup

## Prerequisites

- Docker Desktop (with Compose v2)
- Git
- Node.js 20+ (only if running frontend outside Docker)
- Python 3.11+ (only if running backend outside Docker)

## 1. Configure Environment

```bash
cp .env.example .env
```

Set required values in `.env`:

- `SECRET_KEY`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `GITHUB_REDIRECT_URI` (default local: `http://localhost:3000/auth/callback`)
- `GROQ_API_KEY` (optional for AI generation quality)

## 2. Start Stack

```bash
docker compose up --build -d
```

## 3. Apply Database Migrations

Migrations are auto-run by API/worker startup, but can be run manually:

```bash
docker compose exec api alembic upgrade head
```

## 4. Open Services

- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Flower: `http://localhost:5555`

## Useful Commands

```bash
# service status
docker compose ps

# API logs
docker compose logs -f api

# Worker logs
docker compose logs -f celery-worker

# stop all services
docker compose down
```
