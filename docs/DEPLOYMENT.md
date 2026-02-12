# Deployment Guide

DevForge is designed for local-first development, then cloud rollout.

## Target Platforms

- Frontend: Vercel
- Backend worker/API: Railway
- Postgres: Supabase or Railway Postgres
- Redis: Upstash

## Environment Variables

Configure the same keys from `.env.example` in each platform.

Critical production variables:

- `SECRET_KEY` (strong random value)
- `DEBUG=false`
- `DATABASE_URL`
- `SYNC_DATABASE_URL`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `GITHUB_REDIRECT_URI` (frontend deployed callback URL)
- `NEXT_PUBLIC_API_URL` (frontend)
- `NEXT_PUBLIC_WS_URL` (frontend)

## Frontend (Vercel)

1. Import repository into Vercel.
2. Set root directory to `frontend`.
3. Add frontend environment variables.
4. Deploy.

## Backend/API + Workers (Railway)

1. Create a Railway project from this repo.
2. Create three services using the same `backend` source:
   - API (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
   - Celery worker (`celery -A app.tasks.celery_app.celery_app worker --loglevel=info`)
   - Celery beat (`celery -A app.tasks.celery_app.celery_app beat --loglevel=info`)
3. Add shared environment variables to all services.
4. Run migration job:
   - `alembic upgrade head`

## Post-Deploy Checks

- `GET /health` returns `200`.
- OAuth callback works from frontend.
- GitHub sync task enqueues and is visible in worker logs.
- Portfolio generation creates output and progress events.
