# API Overview

Base path: `/api`

## Auth

- `POST /auth/github`
- `GET /auth/github/callback`
- `POST /auth/logout`
- `GET /auth/me`

## Users

- `GET /users/me`
- `PATCH /users/me`
- `DELETE /users/me`

## GitHub

- `POST /github/sync`
- `GET /github/sync/status`
- `GET /github/profile`
- `GET /github/repositories`
- `GET /github/repos/{id}`

## Public (No Auth)

- `POST /public/generate` (input: GitHub URL/username, output: generated portfolio URL)

## Portfolios

- `GET /portfolios`
- `POST /portfolios`
- `GET /portfolios/{id}`
- `PATCH /portfolios/{id}`
- `DELETE /portfolios/{id}`
- `POST /portfolios/{id}/generate`
- `GET /portfolios/{id}/preview`
- `GET /portfolios/{id}/events` (SSE stream)

## Templates

- `GET /templates`
- `GET /templates/{id}`
- `POST /templates/{id}/customize`

## Analytics

- `GET /analytics/{portfolio_id}`
- `POST /analytics/track`

## Health

- `GET /health`
- `GET /health/ready`
- `GET /metrics`
