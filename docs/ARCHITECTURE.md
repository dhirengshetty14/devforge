# DevForge Architecture

## High-Level

- `frontend` (Next.js) calls backend REST APIs and subscribes to realtime generation events.
- `api` (FastAPI) handles auth, data APIs, and orchestration commands.
- `celery-worker` executes distributed data processing and generation tasks.
- `postgres` stores canonical state, analytics, and persistent cache.
- `redis` serves as broker, hot cache, pub/sub bus, and rate-limit store.

## Processing Model

1. User triggers sync/generation.
2. API creates `generation_jobs` record and enqueues Celery workflow.
3. Workers run map-reduce style commit analysis and AI enrichment.
4. Worker publishes progress events to Redis pub/sub and persists checkpoints.
5. API/WebSocket stream pushes job updates to frontend.

## Reliability

- Idempotent upserts for GitHub sync.
- Retry with backoff for external APIs.
- Circuit-breaker style fail-fast wrapper for unstable dependencies.
- Cache hierarchy:
  - L1 Redis TTL (hot)
  - L2 Postgres persisted snapshot
  - L3 incremental recompute on new commits only

## Scalability

- Stateless API; horizontal scaling ready.
- Celery worker pool scales independently.
- Batch partitioning for commit analysis.
- DB indexes and JSONB GIN indexes for query-heavy endpoints.
