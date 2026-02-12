from __future__ import annotations

import json
from datetime import timedelta

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.repository import Repository
from app.utils.helpers import utcnow

settings = get_settings()


class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get_json(self, key: str) -> dict | list | None:
        payload = await self.redis.get(key)
        if payload is None:
            return None
        return json.loads(payload)

    async def set_json(self, key: str, value: dict | list, ttl_seconds: int | None = None) -> None:
        serialized = json.dumps(value)
        if ttl_seconds:
            await self.redis.setex(key, ttl_seconds, serialized)
        else:
            await self.redis.set(key, serialized)

    async def get_repository_analysis(
        self,
        db: AsyncSession,
        repository_id: str,
        compute_cb,
    ) -> dict:
        # L1 Redis cache
        key = f"{settings.redis_cache_prefix}repo:{repository_id}:analysis"
        cached = await self.get_json(key)
        if cached:
            return cached

        # L2 persisted cache (repository metadata if analyzed recently)
        repo = await db.scalar(select(Repository).where(Repository.id == repository_id))
        if repo and repo.analyzed_at and (utcnow() - repo.analyzed_at) < timedelta(hours=settings.db_cache_ttl_hours):
            data = {
                "repository_id": str(repo.id),
                "name": repo.name,
                "languages": repo.languages,
                "topics": repo.topics,
                "stars": repo.stars,
            }
            await self.set_json(key, data, settings.cache_ttl_seconds)
            return data

        # L3 expensive compute callback
        fresh = await compute_cb()
        await self.set_json(key, fresh, settings.cache_ttl_seconds)
        return fresh
